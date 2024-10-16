# project_manager.py
import json
import os


class ProjectManager:
    def __init__(self, user_stories_file='user_stories.json'):
        self.user_stories_file = user_stories_file
        if not os.path.exists(self.user_stories_file):
            with open(self.user_stories_file, 'w') as f:
                json.dump([], f)

    def load_user_stories(self):
        with open(self.user_stories_file, 'r') as f:
            return json.load(f)

    def save_user_stories(self, stories):
        with open(self.user_stories_file, 'w') as f:
            json.dump(stories, f, indent=2)

    # User Story CRUD operations
    def create_user_story(self, user_story):
        stories = self.load_user_stories()
        new_id = stories[-1]['id'] + 1 if stories else 1
        new_story = {
            'id': new_id,
            'user_story': user_story,
            'subtasks': []
        }
        stories.append(new_story)
        self.save_user_stories(stories)
        return new_id

    def read_user_story(self, user_story_id):
        stories = self.load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                return story
        return None

    def update_user_story(self, user_story_id, user_story):
        stories = self.load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                story['user_story'] = user_story
                self.save_user_stories(stories)
                return True
        return False

    def delete_user_story(self, user_story_id):
        stories = self.load_user_stories()
        for i, story in enumerate(stories):
            if story['id'] == user_story_id:
                del stories[i]
                self.save_user_stories(stories)
                return True
        return False

    # Subtask CRUD operations
    def create_subtask(self, user_story_id, subtask):
        stories = self.load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                new_subtask_id = len(story['subtasks']) + 1
                story['subtasks'].append({'id': new_subtask_id, 'subtask': subtask})
                self.save_user_stories(stories)
                return new_subtask_id
        return None

    def read_subtask(self, user_story_id, subtask_id):
        stories = self.load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                for subtask in story['subtasks']:
                    if subtask['id'] == subtask_id:
                        return subtask
        return None

    def update_subtask(self, user_story_id, subtask_id, subtask):
        stories = self.load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                for st in story['subtasks']:
                    if st['id'] == subtask_id:
                        st['subtask'] = subtask
                        self.save_user_stories(stories)
                        return True
        return False

    def delete_subtask(self, user_story_id, subtask_id):
        stories = self.load_user_stories()
        for story in stories:
            if story['id'] == user_story_id:
                for i, st in enumerate(story['subtasks']):
                    if st['id'] == subtask_id:
                        del story['subtasks'][i]
                        self.save_user_stories(stories)
                        return True
        return False
