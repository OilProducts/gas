# agents/agent.py
import requests
import logging
import json
from .prompt import PromptManager

class AgentError(Exception):
    pass

class Agent:
    def __init__(self,
                 model_name=None,
                 role="Unconfigured Agent",
                 system_message="",
                 is_human=False,
                 model_endpoint="http://127.0.0.1:11434/api/generate",
                 tools=None,
                 log_dir='logs'):
        self.model_name = model_name
        self.model_endpoint = model_endpoint
        self.role = role
        self.system_message = system_message
        self.is_human = is_human
        self.tools = tools or {}
        self.log = logging.getLogger(role)
        # Initialize PromptManager
        self.prompt_manager = PromptManager(
            role=self.role,
            system_content=self.system_message,
            tools=self.tools
        )
        self.log_file = f"{log_dir}/{role}.json"

    def execute_tool(self, tool_call):
        """
        Executes the tool specified in the tool_call.
        """
        tool_name = tool_call['tool']
        args = tool_call['args']

        # Find the tool in self.tools
        tool = self.tools.get(tool_name)
        if not tool:
            self.log.error(f"Tool {tool_name} not found.")
            acknowledgment = f"{self.role} failed to execute tool {tool_name} because the tool was not found."
            self.add_observed_message(f'{self.role}', acknowledgment)
            return acknowledgment

        # Get the function to call
        function = tool['function']

        # Prepare the arguments
        expected_args = tool['args']
        # Convert args to the expected types
        converted_args = {}
        for arg_name, arg_type in expected_args.items():
            if arg_name not in args:
                self.log.error(f"Argument {arg_name} is missing for tool {tool_name}.")
                acknowledgment = f"{self.role} failed to execute tool {tool_name} because argument {arg_name} is missing."
                self.add_observed_message(f'{self.role}', acknowledgment)
                return acknowledgment
            arg_value = args[arg_name]
            # Convert the arg_value to the expected type
            try:
                if arg_type == "int":
                    converted_args[arg_name] = int(arg_value)
                elif arg_type == "str":
                    converted_args[arg_name] = str(arg_value)
                else:
                    converted_args[arg_name] = arg_value  # No conversion
            except ValueError:
                self.log.error(f"Argument {arg_name} has invalid type for tool {tool_name}.")
                acknowledgment = f"{self.role} failed to execute tool {tool_name} because argument {arg_name} has invalid type."
                self.add_observed_message(f'{self.role}', acknowledgment)
                return acknowledgment
        # Call the function
        try:
            result = function(**converted_args)
            acknowledgment = f"{self.role} executed tool {tool_name} successfully."
            # If the function returns a value, include it in the acknowledgment
            if result is not None:
                acknowledgment += f" Result: {result}"
            self.add_observed_message(f'{self.role}', acknowledgment)
            return acknowledgment
        except Exception as e:
            self.log.error(f"Error executing tool {tool_name}: {e}")
            acknowledgment = f"{self.role} failed to execute tool {tool_name} due to an error."
            self.add_observed_message(f'{self.role}', acknowledgment)
            return acknowledgment

    def retain_floor(self):
        """
        Determines if the agent should retain the floor and captures their thought process.
        """
        # Update the conversation history in PromptManager
        # self.prompt_manager.add_observed_message('user', context)

        # Build the prompt
        prompt = self.prompt_manager.get_prompt()
        self.log.debug(f"Prompt for should_respond:\n{prompt}")

        # Add decision-making instruction
        decision_instruction = (
            f"Considering the above conversation, should I, as the {self.role}, take action ("
            f"either a response, or call a tool, etc.) or provide a decision at this point? "
            "Provide a short summary of your reasoning and conclude with 'Decision: Yes' or 'Decision: No'."
        )
        prompt += decision_instruction

        # Prompt the model
        response_text = self.prompt_model(prompt)
        self.log.debug(f"{self.role} thoughts: {response_text}")
        self.add_observed_message(f'{self.role}_thoughts', response_text)


        # Extract the decision
        decision = 'no'
        if 'decision: yes' in response_text.lower():
            decision = 'yes'
        elif 'decision: no' in response_text.lower():
            decision = 'no'
        print(f"{self.role} decision: {decision}")
        return decision == 'yes', response_text
    
    def take_turn(self, context):
        """
        Takes a single turn, which may be multiple rounds of thought and response generation.
        """
        while True:
            retain, thought_process = self.retain_floor()
            if retain:
                response = self.generate_response()
                self.add_observed_message(f'{self.role}', response)
                return response
            else:
                # Add the thought process to the conversation history
                self.add_observed_message(f'{self.role}', thought_process)

    def generate_response(self):
        """
        Generates a response based on the context.
        """
        # Update the conversation history
        # self.prompt_manager.add_observed_message('user', context)
        # Get the prompt
        prompt = self.prompt_manager.get_prompt()
        self.log.debug(f"Prompt for generate_response:\n{prompt}")

        # Prompt the model
        response_text = self.prompt_model(prompt)
        self.log.debug(f"{self.role} response: {response_text}")

        # Parse the response to extract tool calls
        tool_calls = self.parse_tool_calls(response_text)
        if tool_calls:
            acknowledgments = []
            for tool_call in tool_calls:
                # Execute each tool
                acknowledgment = self.execute_tool(tool_call)
                acknowledgments.append(acknowledgment)
            # Optionally, you can add a combined acknowledgment message
            combined_acknowledgment = "\n".join(acknowledgments)
            self.add_observed_message(f'{self.role}', combined_acknowledgment)
            return combined_acknowledgment
        else:
            # Add the assistant's response to the conversation history
            self.add_observed_message(f'{self.role}', response_text)
            return response_text

    def prompt_model(self, prompt):
        """
        Prompts the model with the given prompt.
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "num_predict": 1500  # Adjust as needed
            },
            "stream": False
        }
        try:
            response = requests.post(self.model_endpoint, json=payload)
            response.raise_for_status()
            response_json = response.json()
            response_text = response_json.get('response', '')
            print(f"{self.role} response: {response_text}")
            return response_text.strip()
        except requests.exceptions.RequestException as e:
            self.log.error(f"Request failed: {e}")
            raise AgentError(f"Request failed: {e}")

    def add_observed_message(self, role, message):
        self.prompt_manager.add_observed_message(role, message)

        # load json message history and append new message
        try:
            with open(self.log_file, 'r+') as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    print('No messages found')
                    messages = []
                messages.append({
                    'role': role,
                    'message': message
                })
                f.seek(0)
                f.write(json.dumps(messages))
                f.truncate()
        except FileNotFoundError:
            with open(self.log_file, 'w') as f:
                messages = [{
                    'role': role,
                    'message': message
                }]
                f.write(json.dumps(messages))

    def parse_tool_calls(self, response_text):
        """
        Parses the response text to extract and return a list of tool calls.
        """
        import re

        # Remove special tokens
        response_cleaned = response_text
        tokens_to_remove = [
            "<|start_header_id|>", "<|end_header_id|>",
            "<|python_tag|>", "<|eot_id|>", "<|end_of_text|>", "<|begin_of_text|>"
        ]
        for token in tokens_to_remove:
            response_cleaned = response_cleaned.replace(token, '')

        # Strip leading and trailing whitespace
        response_cleaned = response_cleaned.strip()

        # Split the response by semicolons to get individual tool calls
        tool_call_strings = [s.strip() for s in response_cleaned.split(';') if s.strip()]

        tool_calls = []
        for tool_str in tool_call_strings:
            try:
                # Parse the JSON object
                tool_call = json.loads(tool_str)
                if 'tool' in tool_call and 'args' in tool_call:
                    tool_calls.append(tool_call)
                else:
                    self.log.warning(f"Invalid tool call format: {tool_str}")
            except json.JSONDecodeError as e:
                self.log.warning(f"JSON decode error: {e} for string: {tool_str}")
                continue  # Skip invalid JSON strings
        return tool_calls

    # You can remove or adjust these methods as per your implementation
    def save_context(self):
        pass

    def load_context(self):
        pass

    @staticmethod
    def load_role_definitions():
        # This method may not be needed anymore
        pass

    def get_system_message(self):
        # Already provided during initialization
        return self.system_message
