# app.py
import json
import os
from pathlib import Path
import tomllib
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, _dash_renderer, callback, Input, Output, State
from dash_iconify import DashIconify

_dash_renderer._set_react_version("18.2.0")

# Initialize the app
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)


def load_projects():
    """Load the projects from the data/projects directory"""
    projects = []
    p = Path('data/projects')
    project_dirs = [x for x in p.iterdir() if x.is_dir()]
    for dir in project_dirs:
        with open(os.path.join(dir, 'project.json'), 'r') as f:
            projects.append(json.load(f))
    return {project['project_name']: project for project in projects}


@callback(
    Output('app-shell-navbar', 'children'),
    Input('navbar-content-store', 'data')
)
def create_navbar(navbar_content):
    print(navbar_content)
    projects = load_projects()

    project_links = [
        dmc.NavLink(
            label=project['project_name'],
            href=f"/project/{project['project_name']}",
        ) for project_name, project in projects.items()
    ]

    # Add a link to add a new project
    project_links.append(
        dmc.NavLink(
            label="Add Project",
            href="/add_project",
            leftSection=[DashIconify(icon="ic:baseline-plus", width=16, height=16)]
        )
    )

    navbar = [
        dmc.NavLink(
            label="Agent Templates",
            href="/agent_templates",
            leftSection=[DashIconify(icon="mdi:user-add-outline", width=16, height=16)]
        ),
        dmc.NavLink(
            label="Events",
            href="/events",
            leftSection=[DashIconify(icon="mdi:event-add", width=16, height=16)]
        ),
        dmc.ScrollArea(
            project_links,
            style={'height': '90vh'}
        )
    ]
    return navbar


app.layout = dmc.MantineProvider([
    dmc.AppShell(
        children=[
            dmc.AppShellHeader("GAS"),
            dmc.AppShellNavbar(id='app-shell-navbar', children=create_navbar('')),
            dmc.AppShellMain(dash.page_container,
                             id='page-content'),
        ],
        header={'height': 60},
    ),
    dcc.Store(id='navbar-content-store', data=''),
])

if __name__ == '__main__':
    app.run(debug=True)
