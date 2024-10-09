# pages/add_project.py
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
import json
import os

dash.register_page(__name__, path="/add_project")

def layout():
    print(f'{__file__}layout')
    return dmc.Container([
        # dcc.Location(id='redirect', refresh=True),
        dmc.Title("Add New Project", order=2),
        dmc.Space(h=20),
        dmc.TextInput(
            id='project-name-input',
            label='Project Name',
            placeholder='Enter project name',
            required=True,
        ),
        dmc.Textarea(
            id='project-description-input',
            label='Project Description',
            placeholder='Enter project description',
        ),
        dmc.Space(h=20),
        dmc.Group([
            dmc.Button('Add Project', id='add-project-button'),
            dmc.Text(id='add-project-confirmation',),
        ]),
    ])

@callback(
    Output('add-project-confirmation', 'children'),
    Output('project-name-input', 'value'),
    Output('project-description-input', 'value'),
    Input('add-project-button', 'n_clicks'),
    State('project-name-input', 'value'),
    State('project-description-input', 'value'),
    prevent_initial_call=True
)
def add_new_project(n_clicks, project_name, project_description):
    if n_clicks and project_name:
        projects_file = './templates/projects.json'
        projects = []
        if os.path.exists(projects_file):
            with open(projects_file, 'r') as f:
                projects = json.load(f)
        # Check if the project already exists
        if any(p['name'] == project_name for p in projects):
            return f"Project '{project_name}' already exists.", dash.no_update, dash.no_update
        # Add the new project
        projects.append({
            "name": project_name,
            "description": project_description or ''
        })
        with open(projects_file, 'w') as f:
            json.dump(projects, f, indent=2)
        return f"Project '{project_name}' added successfully.", '', ''
    return '', dash.no_update, dash.no_update


@callback(
    Output('redirect', 'href'),
    Input('add-project-button', 'n_clicks'),
    State('project-name-input', 'value'),
    prevent_initial_call=True
)
def redirect_after_add(n_clicks, project_name):
    if n_clicks and project_name:
        return '/'
    return dash.no_update
