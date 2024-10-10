# pages/add_project.py
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
import json
import os

dash.register_page(__name__, path="/add_project")


def layout():
    return dmc.Container([
        dcc.Location(id='redirect', refresh=True),
        dmc.Title("Add New Project", order=2),
        dmc.Space(h=20),
        dmc.TextInput(
            id='project-name-input',
            label='Project Name',
            placeholder='Enter project name',
            required=True,
            value='New Project',
        ),
        dmc.Textarea(
            id='project-description-input',
            label='Project Description',
            placeholder='Enter project description',
            value='This is a new project.',
        ),
        dmc.Space(h=20),
        dmc.Group([
            dmc.Button('Add Project', id='add-project-button'),
            dmc.Text(id='add-project-confirmation', ),
        ]),
    ])


@callback(
    Output('add-project-confirmation', 'children'),
    Output('project-name-input', 'value'),
    Output('project-description-input', 'value'),
    Output('navbar-projects-store', 'data'),
    Input('add-project-button', 'n_clicks'),
    State('project-name-input', 'value'),
    State('project-description-input', 'value'),
    State('navbar-projects-store', 'data'),
    prevent_initial_call=True
)
def add_new_project(n_clicks, project_name, project_description, navbar_projects):
    if n_clicks and project_name:
        projects_dir = './data/projects'
        if not os.path.exists(projects_dir):
            os.mkdir(projects_dir)

        # Create a directory for the new project
        project_dir = os.path.join(projects_dir, project_name)
        os.mkdir(project_dir)
        project_events_dir = os.path.join(project_dir, 'events')
        os.mkdir(project_events_dir)

        with open(os.path.join(project_dir, 'project.json'), 'w') as f:
            json.dump({
                "project_name": project_name,
                "description": project_description or ''
            }, f, indent=2)
        print('returning from add_new_project')
        navbar_projects.append(project_name)
        return (f"Project {project_name} added successfully.", 'project_name_input',
                ['ok'])
    return '', '', '', navbar_projects


@callback(
    Output('redirect', 'href'),
    Input('add-project-button', 'n_clicks'),
    State('project-name-input', 'value'),
    prevent_initial_call=True
)
def redirect_after_add(n_clicks, project_name):
    if n_clicks and project_name:
        return '/'
    return '/'
