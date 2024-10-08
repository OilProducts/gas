# pages/conduct_event.py
import json
import datetime
import os

import dash
from dash import dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from utils.agent_load import load_agents
from utils.event_load import load_events
# from gas.prompt_manager import PromptManager
# from gas.worker import Worker

dash.register_page(__name__, path='/conduct_event')

# Global variables to store the event and conversation history
event = None
conversation_history = []

# Load agents and events
agents = load_agents()
events_config = load_events()
event_names = list(events_config.keys())

layout = dmc.Container([
    dmc.Title('Conduct Event', order=2, mb=20),
    dmc.Group([
        dmc.Select(
            id='event-selector',
            label='Select an event to start',
            data=[{'label': name, 'value': name} for name in event_names],
            placeholder='Select an event',
            style={'width': '300px'},
        ),
        dmc.Button('Start Event', id='start-event-button', n_clicks=0),
    ]),
    html.Hr(),
    dmc.ScrollArea(
        dmc.Stack(id='conversation-thread'),
        style={'height': '60vh', 'overflow-y': 'auto', 'margin-bottom': '20px'},
    ),
    dmc.Group([
        dmc.Textarea(
            id='user-input',
            placeholder='Enter your message here',
            minRows=3,
            maxRows=3,
            style={'width': '80%'},
        ),
        dmc.Button('Send', id='send-button', n_clicks=0),
    ], justify='center'),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every second
        n_intervals=0
    ),
])

# Callback to start the event
@callback(
    Output('conversation-thread', 'children', allow_duplicate=True),
    Output('start-event-button', 'disabled'),
    Input('start-event-button', 'n_clicks'),
    State('event-selector', 'value'),
    prevent_initial_call=True
)
def start_event(n_clicks, selected_event):
    if n_clicks > 0 and selected_event:
        global event, conversation_history
        conversation_history = []
        event = initialize_event(selected_event)
        # Add initial message indicating the event has started
        conversation_history.append({
            'sender': 'System',
            'message': f'Event "{selected_event}" has started.',
            'timestamp': datetime.datetime.now().isoformat(),
        })
        return format_conversation(conversation_history), True
    else:
        raise PreventUpdate

# Function to initialize the event and participants
def initialize_event(event_name):
    event_config = events_config.get(event_name)
    if not event_config:
        return None

    participants = []
    for role in event_config['participants']:
        agent = agents.get(role)
        if agent:
            participants.append(agent)
        else:
            print(f"Agent for role '{role}' not found.")
    return {
        'name': event_name,
        'description': event_config.get('description', ''),
        'participants': participants
    }

# Callback to handle user input
@callback(
    Output('conversation-thread', 'children'),
    Output('user-input', 'value'),
    Input('send-button', 'n_clicks'),
    State('user-input', 'value'),
    prevent_initial_call=True
)
def handle_user_input(n_clicks, user_input):
    if n_clicks > 0 and user_input:
        global event, conversation_history
        print(event)
        if event is None:
            return conversation_history, ''
        # Assume the first human participant is the user
        human_participant = next((p for p in event['participants'] if p.is_human), None)
        if not human_participant:
            # If no human participant is defined, treat the user as an external input
            sender = 'User'
        else:
            sender = human_participant['role']

        # Add user's message to conversation history
        conversation_history.append({
            'sender': sender,
            'message': user_input,
            'timestamp': datetime.datetime.now().isoformat(),
        })

        # Process agent responses
        process_agent_responses()

        # Update the conversation thread
        return format_conversation(conversation_history), ''
    else:
        raise PreventUpdate

# Function to process agent responses
def process_agent_responses():
    global event, conversation_history
    if event is None:
        return
    # Get the latest conversation context
    context = '\n'.join([f"{entry['sender']}: {entry['message']}" for entry in conversation_history])
    for agent in event['participants']:
        if agent.is_human:
            continue  # Skip human participants
        role = agent.role
        # Determine if the agent should respond
        should_respond, thought_process = agent.should_respond(context)
        if should_respond:
            # Generate response
            response = agent.generate_response(context)
            # Add the agents response to the observations of all agents present
            for p in event['participants']:
                if p.role != role:
                    p.prompt_manager.add_observed_message(role, response)
            # Add agent's response to conversation history
            conversation_history.append({
                'sender': role,
                'message': response,
                'timestamp': datetime.datetime.now().isoformat(),
                'internal_thought': thought_process
            })
        else:
            # Agent decided not to respond
            conversation_history.append({
                'sender': role,
                'message': None,
                'timestamp': datetime.datetime.now().isoformat(),
                'internal_thought': thought_process
            })

        # Write conversation history to project file
        project_file = f'./config/projects.json'
        if os.path.exists(project_file):
            with open(project_file, 'w') as f:
                projects = json.load(f)
            projects['Project Alpha']['events']['Sprint Planning']['conversation_history'] = (
                conversation_history)


# Callback to update the conversation thread periodically
@callback(
    Output('conversation-thread', 'children', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def update_conversation(n_intervals):
    global conversation_history
    return format_conversation(conversation_history)

# Function to format the conversation for display
def format_conversation(conversation_history):
    formatted_conversation = []
    for entry in conversation_history:
        sender = entry['sender']
        message = entry.get('message')
        internal_thought = entry.get('internal_thought', '')
        timestamp = entry.get('timestamp', '')
        if message:
            content = [
                dmc.Text(f"{sender}:"),
                dcc.Markdown(message),
                dcc.Markdown(f"Thoughts: {internal_thought}", style={'color': 'grey'})
            ]
        else:
            content = [
                dmc.Text(f"{sender} decided not to respond.", style={'color': 'grey'}),
                dcc.Markdown(f"Thoughts: {internal_thought}", style={'color': 'grey'})
            ]
        message_div = dmc.Paper(
            content,
            shadow='sm',
            radius='md',
            p='sm',
            withBorder=True,
            mb=10,
        )
        formatted_conversation.append(message_div)
    return formatted_conversation
