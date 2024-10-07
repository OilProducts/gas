import requests
import logging
import json
from abc import ABC, abstractmethod

class AgentError(Exception):
    pass

class Agent:
    """
    A generic Agent class that interacts with the Ollama API.
    Subclasses should implement specific roles like ScrumMaster, ProductOwner, etc.
    """

    def __init__(self,
                 model_name=None,
                 role="Unconfigured Agent",
                 system_message="",
                 is_human=False,
                 model_endpoint="http://192.168.1.137:11434/api/generate"):
        """
        Initialize the Worker with a specific model.

        Parameters:
            model_name (str): The name of the model to use for generation.
            is_human (bool): Flag to indicate if the worker is human-controlled.
        """
        self.model_name = model_name
        self.model_endpoint = model_endpoint
        self.role = role
        self.system_message = system_message
        self.is_human = is_human
        self.log = logging.getLogger(role)

    def should_respond(self, context):
        """
        Determines if the agent should respond and captures their thought process.

        Parameters:
            context (str): The conversation history to provide context.

        Returns:
            Tuple[bool, str]: A tuple containing the decision (True/False) and the thought process.
        """
        prompt = (
            f"{context}\n"
            f"Considering the above conversation, should I, as the {self.role}, respond at this point? "
            "Provide a short summary of your reasoning and conclude with 'Decision: Yes' or "
            "'Decision: No'."
        )

        try:
            response_text = self.prompt_model(prompt)
        except AgentError as e:
            self.log.error(f"Error prompting model: {e}")
            return False, "Error prompting model"

        self.log.debug(
            f"{self.role} thoughts: {response_text}")

        # Extract the decision and thought process
        decision = 'no'
        if 'decision: yes' in response_text.lower():
            decision = 'yes'
        elif 'decision: no' in response_text.lower():
            decision = 'no'
        print(f"{self.role} decision: {decision}")
        return decision == 'yes', response_text

    def prompt_model(self, context):
        """
        Prompts the model with the given context.

        Parameters:
            context (str): The context to provide to the model.

        Returns:
            str: The model's response.
        """
        payload = {
            "model": self.model_name,
            "prompt": context,
            "system": self.get_system_message(),
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1500  # Adjust as needed
            },
            "stream": True
        }

        try:
            response = requests.post(f'{self.model_endpoint}/api/generate', json=payload)
            response.raise_for_status()
            response_text = ""
            for line in response.iter_lines():
                body = json.loads(line)
                response_part = body.get('response', '')
                print(response_part, end='', flush=True)
                response_text += response_part
            self.log.debug(f"Prompted model with context:\n{context}")
            return response_text
        except requests.exceptions.RequestException as e:
            self.log.error(f"Request failed: {e}")
            raise AgentError(f"Request failed: {e}")

    # Placeholder methods for context management
    def save_context(self):
        """
        Saves the current context to a persistent storage.
        """
        pass  # Implement as needed

    def load_context(self):
        """
        Loads the context from persistent storage.
        """
        pass  # Implement as needed

    @staticmethod
    def load_role_definitions():
        with open('roles.json', 'r') as f:
            role_definitions = json.load(f)
        return role_definitions

    def get_system_message(self):
        role_definitions = self.load_role_definitions()
        return role_definitions.get(self.role, {}).get('system_message', '')