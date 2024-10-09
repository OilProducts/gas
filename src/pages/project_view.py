# pages/project_view.py
import urllib

import dash
from dash import html, dcc, callback, Output, Input, State, MATCH, ALL
import dash_mantine_components as dmc
import json
import os

# import pages.conduct_event

dash.register_page(__name__, path_template="/project/<project_name>")

def layout(project_name=None):
    print(f'{__file__}layout')

    project_name = urllib.parse.unquote(project_name)
    return dmc.Container([
        dmc.Title(f"Project: {project_name}", order=2),
        dmc.Space(h=20),
        # dmc.Tabs(
        #     id='events-tabs',
        #     active_tab='events',
        #     children=[
        #         dmc.TabsList([
        #             dmc.TabsTab(label='Events', value='events'),
        #         ]),
        #     ],
        # ),

        dmc.Group([
            dmc.Button('Add Event',
                       id='add-event-button',
                       href=f"/project/{project_name}/add_event",
                       n_clicks=0),
        ]),
        dmc.Space(h=20),
        dcc.Store(id='project-name-store', data=project_name),
        dcc.Store(id='events-store'),
        dmc.Tabs(None, id='events-tabs'),
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
    if events:
        tabs = [
            dmc.TabsTab(event_name, value=event_name) for event_name, event in events.items()
        ]
        return [
            dmc.TabsList(children=tabs),
        ]
    else:
        return [html.Div("No events found. Please add an event.")]

@callback(
    Output('event-content', 'children'),
    Input('events-tabs', 'value'),
    State('events-store', 'data'),
)
def display_event_content(selected_event, events):
    if selected_event and events:
        event = events[selected_event]
        if event:
            return html.Div([
                dmc.Text(f"Event: {event['name']}"),
                dmc.Text(f"Description: {event['description']}"),
                # Add more event details or functionalities here
            ])
    return html.Div("Select an event to view details.")
