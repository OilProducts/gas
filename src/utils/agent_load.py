# utils/agent_load.py
import json
import os
from agents.agent import Agent

def load_agents():
    AGENTS_CONFIG_FILE = './config/agents.json'
    if not os.path.exists(AGENTS_CONFIG_FILE):
        print("Agents configuration file not found.")
        return {}

    with open(AGENTS_CONFIG_FILE, 'r') as f:
        agents_config = json.load(f)

    agents = {}
    for role_name, config in agents_config.items():
        agent = Agent(
            model_name=config.get('model_name', 'default_model'),
            role=role_name,
            system_message=config.get('system_message', ''),
            is_human=config.get('is_human', False),
            model_endpoint=config.get('model_endpoint', 'http://localhost:11434/api/generate'),
            tools=config.get('tools', [])
        )
        agents[role_name] = agent
    return agents
