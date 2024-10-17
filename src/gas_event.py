import os
from datetime import datetime
import core

# set a unique log directory for each execution based on HH:MM:SS timestamp
base_log_dir = 'logs'
log_dir = os.path.join(base_log_dir, f'{datetime.now().strftime("%H_%M_%S")}')
os.makedirs(log_dir, exist_ok=True)

# In the main function
scrum_master_tools = core.ScrumMasterTools(log_dir=log_dir)

# scrum_master_tools = {
#     "create_user_story": {
#         "description": "Creates a new user story and returns its unique ID.",
#         "args": {
#             "user_story": "str"
#         },
#         "function": project_manager.create_user_story
#     },
#     "read_user_story": {
#         "description": "Reads a user story identified by user_story_id.",
#         "args": {
#             "user_story_id": "int"
#         },
#         "function": project_manager.read_user_story
#     },
#     "update_user_story": {
#         "description": "Updates an existing user story identified by user_story_id.",
#         "args": {
#             "user_story_id": "int",
#             "user_story": "str"
#         },
#         "function": project_manager.update_user_story
#     },
#     "delete_user_story": {
#         "description": "Deletes a user story identified by user_story_id.",
#         "args": {
#             "user_story_id": "int"
#         },
#         "function": project_manager.delete_user_story
#     },
#     "create_subtask": {
#         "description": "Creates a new subtask under a user story and returns its unique ID.",
#         "args": {
#             "user_story_id": "int",
#             "subtask": "str"
#         },
#         "function": project_manager.create_subtask
#     },
#     "read_subtask": {
#         "description": "Reads a subtask identified by user_story_id and subtask_id.",
#         "args": {
#             "user_story_id": "int",
#             "subtask_id": "int"
#         },
#         "function": project_manager.read_subtask
#     },
#     "update_subtask": {
#         "description": "Updates an existing subtask identified by user_story_id and subtask_id.",
#         "args": {
#             "user_story_id": "int",
#             "subtask_id": "int",
#             "subtask": "str"
#         },
#         "function": project_manager.update_subtask
#     },
#     "delete_subtask": {
#         "description": "Deletes a subtask identified by user_story_id and subtask_id.",
#         "args": {
#             "user_story_id": "int",
#             "subtask_id": "int"
#         },
#         "function": project_manager.delete_subtask
#     }
# }



developer_system_message = ("You are a skilled developer in the team. Collaborate effectively "
                            "with team members and focus on delivering high-quality increments. "
                            "During meetings you are an effective communicator and provide "
                            "valuable insights to the team, including the Scrum Master and "
                            "Product Owner. You thoughtfully evaluate technical proposals from "
                            "the team and are not afraid to ask questions, seek clarification, "
                            "or provide constructive criticism when necessary.")

scrum_master_system_message = ("You are the Scrum Master for the team. You are responsible for "
                               "facilitating the Scrum process and ensuring that the team adheres "
                               "to the Agile principles and practices. You help the team to "
                               "self-organize and make decisions, and you work to remove any "
                               "impediments that are hindering the team's progress. You are a "
                               "servant leader, focused on helping the team to achieve its goals "
                               "and continuously improve. You are also responsible for "
                               "recognizing when a meeting should be ended and ensuring that "
                               "the team stays on track and focused during meetings.  Your most "
                               "important responsibility however, is recording the user stories "
                               "and subtasks that the team decides on during the sprint planning "
                               "meeting.  You will record these using the functions available to you.")

product_owner_system_message = ("You are the Product Owner for the team. You are responsible for "
                                "defining the product vision and prioritizing the product backlog. "
                                "You work closely with the team to ensure that the product backlog "
                                "is well-defined and that the team is working on the most valuable "
                                "items. You are the voice of the customer and are responsible for "
                                "ensuring that the team is delivering value to the customer. "
                                "When the development team has questions about the requirements "
                                "or priorities, you are the one to provide clarification, "
                                "and in the absense of concrete requirements, you provide "
                                "plausible and actionable guidance.")

sprint_planning_system_message = ("Its good to see the whole team here, we have our Developer, "
                                  "our Scrum Master, and the Product Owner participating in this "
                                  "meeting."
                                  "This sprint we will be working on creating a remote "
                                  "administration tool.  This will be a simple tool that will "
                                  "support 'get', 'put', and 'execute' operations on remote "
                                  "machines.  The tool does not need to handle multiple "
                                  "connections.  It should provide a simple command-line interface "
                                  "for users to interact with the remote machines.  The remote end "
                                  "will be written in C, and the client will be written in "
                                  "Python.  We will stick to the python standard library for the "
                                  "client and the C standard library (with posix) for the server.  We will"
                                  "need to define the protocol for communication between the client "
                                  "and server.  We will also need to define the error handling "
                                  "strategy for the tool.  The tool should be able to handle "
                                  "network errors, file errors, and errors related to the remote "
                                  "machine.  We will need to define the error codes and messages "
                                  "that the tool will return to the user in case of an error.  We "
                                  "will also need to define the logging strategy for the tool.  The "
                                  "tool should log all interactions with the remote machine, as well "
                                  "as any errors that occur.  The logs should be stored in a "
                                  "directory on the local machine, python standard library "
                                  "default logging should suffice.  The connections do not need "
                                  "to be encrypted.  Lets start by generating some user stories "
                                  "that we can sub task off of.")

additional_context = ("You are currently participating in a sprint planning meeting.  Your "
                      "thoughts, actions, and responses should be in line with the current "
                      "sprint goals and objectives.  It is not necessary to provide detailed "
                      "technical specifications or implement any features during this meeting.  "
                      "This meeting is scoped to generate user stories and subtasks only.")

def main():
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    # model_name = 'llama3.1:8b-instruct-q8_0'
    model_name = 'llama3.1:70b-instruct-q4_K_M'
    model_endpoint = "http://127.0.0.1:11434/api/generate"

    developer = core.Agent(model_name,
                           'Developer',
                           developer_system_message,
                           additional_context=additional_context,
                           model_endpoint=model_endpoint,
                           log_dir=log_dir)
    scrum_master = core.Agent(model_name,
                              'Scrum Master',
                              scrum_master_system_message,
                              additional_context=additional_context,
                              model_endpoint=model_endpoint,
                              tools=scrum_master_tools.tool_descriptions(),
                              log_dir=log_dir)
    product_owner = core.Agent(model_name,
                               'Product Owner',
                               product_owner_system_message,
                               additional_context=additional_context,
                               model_endpoint=model_endpoint,
                               log_dir=log_dir)
    for agent in [developer, scrum_master, product_owner]:
        agent.add_observed_message('product_owner', sprint_planning_system_message)
    rounds = 0
    while rounds < 3:
        for agent in [developer, scrum_master, product_owner]:
            while True:
                retain, response = agent.take_turn()
                if not retain:
                    print(f'**********{agent.role} decided not to retain the floor.**********')
                    break
                for other_agent in [developer, scrum_master, product_owner]:
                    if other_agent != agent:
                        other_agent.add_observed_message(agent.role, response)
        rounds += 1



if __name__ == '__main__':
    main()
