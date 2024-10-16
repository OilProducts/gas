import json

def record_user_story(user_story):
    """
    Records a user story by appending it to a JSON file.
    Returns the user_story_id.
    """
    filename = 'user_stories.json'
    try:
        with open(filename, 'r') as f:
            stories = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stories = []

    # Generate a unique ID
    new_id = stories[-1]['id'] + 1 if stories else 1

    new_story = {
        'id': new_id,
        'user_story': user_story,
        'subtasks': []
    }
    stories.append(new_story)
    with open(filename, 'w') as f:
        json.dump(stories, f, indent=2)
    print(f"Recorded user story: {user_story} with ID {new_id}")

    # Return the new user_story_id
    return new_id

def record_subtask(user_story_id, subtask):
    """
    Records a subtask under the specified user story.
    """
    filename = 'user_stories.json'
    try:
        with open(filename, 'r') as f:
            stories = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stories = []

    # Find the user story by ID
    for story in stories:
        if story['id'] == user_story_id:
            story['subtasks'].append(subtask)
            break
    else:
        print(f"User story with ID {user_story_id} not found.")
        return

    # Save the updated stories
    with open(filename, 'w') as f:
        json.dump(stories, f, indent=2)
    print(f"Recorded subtask: {subtask} under user story ID {user_story_id}")
