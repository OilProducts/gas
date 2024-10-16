class PromptManager:
    def __init__(self, role, system_content, tools=None):
        self.role = role  # Role of the agent, e.g., 'Scrum Master', 'Developer'
        self.system_content = system_content  # System prompt content
        self.tools = tools or {}  # List of tools available to the agent
        self.special_tokens = {
            "begin_of_text": "<|begin_of_text|>",
            "end_of_text": "<|end_of_text|>",
            "start_header": "<|start_header_id|>",
            "end_header": "<|end_header_id|>",
            "eot": "<|eot_id|>",
            "eom": "<|eom_id|>",
            "python_tag": "<|python_tag|>",
        }
        self.messages = []  # Conversation history

        # Initialize the prompt with the system prompt
        self._initialize_system_prompt()

    def _initialize_system_prompt(self):
        # Construct the system prompt with environment and tools
        if self.tools:
            tools_descriptions = ""
            for tool_name, tool in self.tools.items():
                args = ", ".join(f"{arg}: {type_}" for arg, type_ in tool["args"].items())
                tools_descriptions += f"\n- {tool_name}({args}): {tool['description']}"
            tool_usage_instructions = (
                "You have access to the following tools, which you can use by outputting a JSON object in the following format:\n"
                '{"tool": "tool_name", "args": {"arg1": "value1", "arg2": "value2", ...}}\n'
                "Replace 'tool_name' with the name of the tool, and provide the necessary arguments.\n"
                "Available tools are:"
                f"{tools_descriptions}"
            )
        else:
            tool_usage_instructions = ""
        system_prompt = (
            f"Environment: ipython\n"
            f"{tool_usage_instructions}\n"
            f"Cutting Knowledge Date: December 2023\n"
            f"Today Date: 23 July 2024\n\n"
            f"You are the {self.role}.\n\n"
            f"{self.system_content}"
        )
        self.add_observed_message("system", system_prompt)

    def add_observed_message(self, role, content):
        message = {
            "role": role,
            "content": content.strip()
        }
        self.messages.append(message)

    def get_prompt(self):
        # Build the prompt from the messages
        prompt = self.special_tokens["begin_of_text"]
        for message in self.messages:
            role_token = self.special_tokens['start_header'] + message['role'] + self.special_tokens['end_header']
            content = message['content']
            if message['role'] == 'assistant' and content.startswith(self.special_tokens['python_tag']):
                # If the assistant is providing code, don't add eot or eom here
                prompt += f"{role_token}\n{content}"
            else:
                prompt += f"{role_token}\n\n{content}{self.special_tokens['eot']}"
        # print(prompt)
        return prompt

    def reset(self):
        # Reset messages but keep the system prompt
        self.messages = []
        self._initialize_system_prompt()
