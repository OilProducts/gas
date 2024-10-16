import os

import core

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
                               "and continuously improve.")

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

sprint_planning_system_message = ("This sprint we will be working on creating a remote "
                                  "administration tool.  This will be a simple tool that will "
                                  "support 'get', 'put', and 'execute' operations on remote "
                                  "machines.  The tool should be able to handle multiple "
                                  "connections and provide a simple command-line interface for "
                                  "users to interact with the remote machines.  The remote end "
                                  "will be written in C, and the client will be written in Python. ")

log_dir = 'logs'

def main():
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    developer = core.Agent('llama3.1:8b-instruct-q8_0',
                           'Developer',
                           developer_system_message,
                           model_endpoint="http://192.168.1.137:11434/api/generate")
    scrum_master = core.Agent('llama3.1:8b-instruct-q8_0',
                              'Scrum Master',
                              scrum_master_system_message,
                              model_endpoint="http://192.168.1.137:11434/api/generate")
    product_owner = core.Agent('llama3.1:8b-instruct-q8_0',
                               'Product Owner',
                               product_owner_system_message,
                               model_endpoint="http://192.168.1.137:11434/api/generate")
    for agent in [developer, scrum_master]:
        agent.add_observed_message('product_owner', sprint_planning_system_message)
    rounds = 0
    while rounds < 5:
        for agent in [developer, scrum_master, product_owner]:
            if agent.should_respond():
                response = agent.generate_response()
                for other_agent in [developer, scrum_master, product_owner]:
                    if other_agent != agent:
                        other_agent.add_observed_message(agent.role, response)
        rounds += 1


if __name__ == '__main__':
    main()
