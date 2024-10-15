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

sprint_planning_system_message = ("This sprint we will be working on creating a remote "
                                  "administration tool.  This will be a simple tool that will "
                                  "support 'get', 'put', and 'execute' operations on remote "
                                  "machines.  The tool should be able to handle multiple "
                                  "connections and provide a simple command-line interface for "
                                  "users to interact with the remote machines.  The remote end "
                                  "will be written in C, and the client will be written in Python. ")

def main():
    developer = core.Agent('llama3.1:8b-instruct-q8_0', 'Developer', developer_system_message)
    scrum_master = core.Agent('llama3.1:8b-instruct-q8_0', 'Scrum Master', scrum_master_system_message)

    while True:
        for agent in [developer, scrum_master]:
            agent.add_observed_message('product_owner', sprint_planning_system_message)


        for agent in [developer, scrum_master]:
            if agent.should_respond():
                response = agent.generate_response()
                for other_agent in [developer, scrum_master]:
                    if other_agent != agent:
                        other_agent.add_observed_message(agent.role, response)



if __name__ == '__main__':
    main()
