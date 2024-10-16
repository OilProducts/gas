# pages/project_view.py
import urllib

import dash
from dash import html, dcc, callback, Output, Input, State, MATCH, ALL
import dash_mantine_components as dmc
import json
import os

#from .add_event import layout as add_event_layout

dash.register_page(__name__, path_template="/project/<project_name>")

def layout(project_name=None):
    print(f'{__file__}layout')

    project_name = urllib.parse.unquote(project_name)
    return dmc.Container([
        dmc.Title(f"Project: {project_name}", order=2),
        dmc.Space(h=20),
        # dmc.Group([
        #     dmc.Button('Add Event',
        #                id='add-event-button',
        #                n_clicks=0),
        # ]),
        dmc.Space(h=20),
        dcc.Store(id='project-name-store', data=project_name),
        dcc.Store(id='events-store'),
        dmc.Tabs(None, id='events-tabs', value='Add Event'),
        dmc.Space(h=20),
        html.Div(id='event-content'),
    ])

@callback(
    Output('events-store', 'data'),
    Input('project-name-store', 'data'),
)
def load_events_from_project(project_name):
    project_file = f'./data/projects/{project_name}/project.json'
    if os.path.exists(project_file):
        with open(project_file, 'r') as f:
            project = json.load(f)
        # project_events = {e for e in project['events']}
        return project.get('events', {})
    return {}

@callback(
    Output('events-tabs', 'children'),
    Input('events-store', 'data'),
)
def update_event_tabs(events):
    print(f'update_event_tabs: {events}')
    if events:
        tabs = [
            dmc.TabsTab(event_name, value=event_name) for event_name, event in events.items()
        ]
    else:
        tabs = []

    tabs.append(dmc.TabsTab('Add Event', value='Add Event'))
    print(f'tabs: {tabs}')

    return dmc.TabsList(children=tabs),

@callback(
    Output('event-content', 'children'),
    Input('events-tabs', 'value'),
    State('events-store', 'data'),
    State('project-name-store', 'data'),
)
def display_event_content(selected_event, events, project_name):
    print(f'display_event_content selected_event: {selected_event}')
    if selected_event == 'Add Event':
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
                dmc.Text(id='add-event-confirmation'),
            ]),
        ])
    if selected_event and events:
        event = events[selected_event]
        if event:
            return html.Div([
                dmc.Text(f"Event: {event['name']}"),
                dmc.Text(f"Description: {event['description']}"),
                # Add more event details or functionalities here
            ])
    return html.Div("Select an event to view details.")


@callback(
    Output('event-content', 'children', allow_duplicate=True),
    Input('add-event-button', 'n_clicks'),
    State('project-name-store', 'data'),
    prevent_initial_call=True
)
def add_event_to_project(n_clicks, project_name):
    if n_clicks:
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
                dmc.Text(id='add-event-confirmation'),
            ]),
        ])

@callback(
    Output('add-event-confirmation', 'children'),
    Output('event-name-input', 'value'),
    Output('event-description-input', 'value', allow_duplicate=True),
    Output('events-store', 'data', allow_duplicate=True),
    Input('add-event-button', 'n_clicks'),
    State('event-name-input', 'value'),
    State('event-description-input', 'value'),
    State('project-name-store', 'data'),
    State('events-store', 'data'),
    prevent_initial_call=True
)
def add_event(n_clicks, event_name, event_description, project_name, events):
    if n_clicks and event_name and project_name:
        project_dir = f'./data/{project_name}'
        events_dir = os.path.join(project_dir, 'events')
        event_file = os.path.join(events_dir, f'{event_name}.json')
        if not os.path.exists(events_dir):
            os.makedirs(events_dir)
        if os.path.exists(event_file):
            return f"Event '{event_name}' already exists in '{project_name}'.", dash.no_update, dash.no_update
        with open(event_file, 'w') as f:
            json.dump({
                "name": event_name,
                "description": event_description or '',
                "participants": []
            }, f, indent=2)
            events[event_name] = {
                "name": event_name,
                "description": event_description or '',
                "participants": []
            }
        return f"Event '{event_name}' added to '{project_name}' successfully.", '', '', events
    return '', dash.no_update, dash.no_update, events

    # project_file = f'./data/projects/{project_name}/project.json'
    # if os.path.exists(project_file):
    #     with open(project_file, 'r') as f:
    #         project = json.load(f)
    #     project_events = project.get('events', {})
    #     if event_name in project_events:
    #         return f"Event '{event_name}' already exists in '{project_name}'.", dash.no_update, dash.no_update
    #     project_events[event_name] = {
    #         "name": event_name,
    #         "description": event_description or '',
    #         "participants": []
    #     }
    #     project['events'] = project_events
    #     with open(project_file, 'w') as f:
    #         json.dump(project, f, indent=2)
    #     return f"Event '{event_name}' added successfully.", dash.no_update, dash.no_update
    # return f"Project '{project_name}' not found.", dash.no_update, dash.no_update
