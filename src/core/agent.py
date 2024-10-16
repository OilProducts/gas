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
        self.tools = tools or []
        self.log = logging.getLogger(role)
        # Initialize PromptManager
        self.prompt_manager = PromptManager(
            role=self.role,
            system_content=self.system_message,
            tools=self.tools
        )
        self.log_file = f"{log_dir}/{role}.json"

    def should_respond(self):
        """
        Determines if the agent should respond and captures their thought process.
        """
        # Update the conversation history in PromptManager
        # self.prompt_manager.add_observed_message('user', context)

        # Build the prompt
        prompt = self.prompt_manager.get_prompt()
        self.log.debug(f"Prompt for should_respond:\n{prompt}")

        # Add decision-making instruction
        decision_instruction = (
            f"Considering the above conversation, should I, as the {self.role}, respond at this point? "
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
        print(f"Payload: {payload}")

        try:
            response = requests.post(self.model_endpoint, json=payload)
            response.raise_for_status()
            response_json = response.json()
            response_text = response_json.get('response', '')
            return response_text.strip()
        except requests.exceptions.RequestException as e:
            self.log.error(f"Request failed: {e}")
            # raise AgentError(f"Request failed: {e}")

    def add_observed_message(self, role, message):
        self.prompt_manager.add_observed_message(role, message)

        # load json message history and append new message
        with open(self.log_file, 'w+') as f:
            try:
                messages = json.load(f)
            except json.JSONDecodeError:
                print('No messages found')
                messages = []
            messages.append({
                'role': role,
                'message': message
            })
            f.write(json.dumps(messages))

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
