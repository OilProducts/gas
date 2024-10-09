# utils/event_load.py
import json
import os

def load_events():
    EVENTS_CONFIG_FILE = './templates/events.json'
    if not os.path.exists(EVENTS_CONFIG_FILE):
        print("Events configuration file not found.")
        return {}

    with open(EVENTS_CONFIG_FILE, 'r') as f:
        events_config = json.load(f)
    return events_config
