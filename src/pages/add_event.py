# pages/add_event.py
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
import json
import os

dash.register_page(__name__, path_template="/project/<project_name>/add_event")

def layout(project_name=None):
    return dmc.Container([
        dmc.Title(f"Add Event to {project_name}", order=2),
        dcc.Store(id='project-name-store', data=project_name),
        dmc.Space(h=20),
        dmc.TextInput(
            id='event-name-input',
            label='Event Name',
            placeholder='Enter event name',
            required=True,
        ),
        dmc.Textarea(
            id='event-description-input',
            label='Event Description',
            placeholder='Enter event description',
        ),
        dmc.Space(h=20),
        dmc.Group([
            dmc.Button('Add Event', id='add-event-button'),
            dmc.Text(id='add-event-confirmation', color='green'),
        ]),
    ])

@callback(
    Output('add-event-confirmation', 'children'),
    Output('event-name-input', 'value'),
    Output('event-description-input', 'value'),
    Input('add-event-button', 'n_clicks'),
    State('event-name-input', 'value'),
    State('event-description-input', 'value'),
    State('project-name-store', 'data'),
    prevent_initial_call=True
)
def add_event(n_clicks, event_name, event_description, project_name):
    if n_clicks and event_name and project_name:
        events_file = './config/events.json'
        events = []
        if os.path.exists(events_file):
            with open(events_file, 'r') as f:
                events = json.load(f)
        # Check if the event already exists in the project
        if any(e['name'] == event_name and e['project'] == project_name for e in events):
            return f"Event '{event_name}' already exists in '{project_name}'.", dash.no_update, dash.no_update
        # Add the new event
        events.append({
            "name": event_name,
            "description": event_description or '',
            "project": project_name,
            "participants": []
        })
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=2)
        return f"Event '{event_name}' added to '{project_name}' successfully.", '', ''
    return '', dash.no_update, dash.no_update
