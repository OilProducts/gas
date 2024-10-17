import json
import os
import inspect
from typing import Optional, Dict, Any, List


class ScrumMasterTools:
    def __init__(self, log_dir='./logs'):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.user_stories_file = f'{self.log_dir}/user_stories.json'
        if not os.path.exists(self.user_stories_file):
            with open(self.user_stories_file, 'w') as f:
                json.dump([], f)

    def _load_user_stories(self):
        """Loads user stories from the JSON file."""
        with open(self.user_stories_file, 'r') as f:
            return json.load(f)

    def _save_user_stories(self, stories):
        """Saves user stories to the JSON file."""
        with open(self.user_stories_file, 'w') as f:
            json.dump(stories, f, indent=2)

    # User Story CRUD operations
    def create_user_story(self, user_story: str) -> int:
        """
        Creates a new user story and returns its unique ID.

        Args:
            user_story (str): The user story to create.

        Returns:
            int: The unique ID of the new user story.
        """
        stories = self._load_user_stories()
        new_id = stories[-1]['id'] + 1 if stories else 1
        new_story = {
            'id': new_id,
            'user_story': user_story,
            'subtasks': []
        }
        stories.append(new_story)
        self._save_user_stories(stories)
        return new_id

    def read_user_story(self, user_story_id: int) -> Optional[dict]:
        """
        Reads a user story identified by user_story_id.

        Args:
            user_story_id (int): The ID of the user story to read.

        Returns:
            dict or None: The user story if found, else None.
        """
        stories = self._load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                return story
        return None

    def update_user_story(self, user_story_id: int, user_story: str) -> bool:
        """
        Updates an existing user story identified by user_story_id.

        Args:
            user_story_id (int): The ID of the user story to update.
            user_story (str): The new user story content.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        stories = self._load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                story['user_story'] = user_story
                self._save_user_stories(stories)
                return True
        return False

    def delete_user_story(self, user_story_id: int) -> bool:
        """
        Deletes a user story identified by user_story_id.

        Args:
            user_story_id (int): The ID of the user story to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        stories = self._load_user_stories()
        for i, story in enumerate(stories):
            if story['id'] == user_story_id:
                del stories[i]
                self._save_user_stories(stories)
                return True
        return False

    # Subtask CRUD operations
    def create_subtask(self, user_story_id: int, subtask: str) -> Optional[int]:
        """
        Creates a new subtask under a user story and returns its unique ID.

        Args:
            user_story_id (int): The ID of the user story.
            subtask (str): The subtask to create.

        Returns:
            int or None: The unique ID of the new subtask, or None if user story not found.
        """
        stories = self._load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                new_subtask_id = len(story['subtasks']) + 1
                story['subtasks'].append({'id': new_subtask_id, 'subtask': subtask})
                self._save_user_stories(stories)
                return new_subtask_id
        return None

    def read_subtask(self, user_story_id: int, subtask_id: int) -> Optional[dict]:
        """
        Reads a subtask identified by user_story_id and subtask_id.

        Args:
            user_story_id (int): The ID of the user story.
            subtask_id (int): The ID of the subtask.

        Returns:
            dict or None: The subtask if found, else None.
        """
        stories = self._load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                for subtask in story['subtasks']:
                    if subtask['id'] == subtask_id:
                        return subtask
        return None

    def update_subtask(self, user_story_id: int, subtask_id: int, subtask: str) -> bool:
        """
        Updates an existing subtask identified by user_story_id and subtask_id.

        Args:
            user_story_id (int): The ID of the user story.
            subtask_id (int): The ID of the subtask.
            subtask (str): The new subtask content.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        stories = self._load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                for st in story['subtasks']:
                    if st['id'] == subtask_id:
                        st['subtask'] = subtask
                        self._save_user_stories(stories)
                        return True
        return False

    def delete_subtask(self, user_story_id: int, subtask_id: int) -> bool:
        """
        Deletes a subtask identified by user_story_id and subtask_id.

        Args:
            user_story_id (int): The ID of the user story.
            subtask_id (int): The ID of the subtask.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        stories = self._load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                for i, st in enumerate(story['subtasks']):
                    if st['id'] == subtask_id:
                        del story['subtasks'][i]
                        self._save_user_stories(stories)
                        return True
        return False

    def tool_descriptions(self) -> List[Dict[str, Any]]:
        """Generates a list of tool descriptions in the required JSON format."""
        tools = []
        methods = inspect.getmembers(self, predicate=inspect.isfunction)
        for name, method in methods:
            if name.startswith('_') or name in ['load_user_stories', 'save_user_stories',
                                                'tool_descriptions']:
                continue  # Skip private and helper methods

            doc = inspect.getdoc(method)
            sig = inspect.signature(method)
            required_params = []
            properties = {}

            for param in sig.parameters.values():
                if param.name == 'self':
                    continue
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
                param_type_str = self._get_type_str(param_type)
                param_desc = self._get_param_description(doc, param.name)
                properties[param.name] = {
                    'type': param_type_str,
                    'description': param_desc
                }
                required_params.append(param.name)

            tool = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": self._get_description(doc),
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required_params
                    }
                }
            }
            tools.append(tool)
        return tools

    def _get_description(self, doc: str) -> str:
        """Extracts the first paragraph of the docstring as the description."""
        if doc:
            return doc.strip().split('\n\n')[0]
        return ''

    def _get_param_description(self, doc: str, param_name: str) -> str:
        """Extracts parameter description from the docstring."""
        if not doc:
            return ''
        lines = doc.splitlines()
        in_args = False
        for line in lines:
            if line.strip().startswith('Args:'):
                in_args = True
                continue
            if in_args:
                if line.strip() == '':
                    break  # End of Args section
                if line.strip().startswith(param_name):
                    # Expected format: param_name (type): description
                    parts = line.strip().split(':', 1)
                    if len(parts) == 2:
                        return parts[1].strip()
        return ''

    def _get_type_str(self, param_type: Any) -> str:
        """Converts a type annotation to a JSON schema type."""
        type_mappings = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            dict: 'object',
            list: 'array',
            Optional[str]: 'string',
            Optional[int]: 'integer',
            Any: 'any'
        }
        return type_mappings.get(param_type, 'string')

# Usage example
# if __name__ == "__main__":
#     project_manager = ScrumMasterTools()
#     scrum_master_tools = project_manager.tool_descriptions()
#     print(json.dumps({k: {'description': v['description'], 'args': v['args']} for k, v in scrum_master_tools.items()}, indent=2))
