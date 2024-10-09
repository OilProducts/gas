# app.py
import json
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, _dash_renderer, callback, Input, Output, State
from dash_iconify import DashIconify


_dash_renderer._set_react_version("18.2.0")

# Initialize the app
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

def load_projects():
    with open('templates/projects.json', 'r') as f:
        projects = json.load(f)
    return projects

def create_navbar():
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
    print(project_links)

    navbar = dmc.AppShellNavbar(
        children=[
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
        ],
    )
    return navbar

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        children=[
            dmc.AppShellHeader("GAS"),
            create_navbar(),
            dmc.AppShellMain(dash.page_container,
                             id='page-content'),
        ],
        header={'height': 60},
    ),
)

if __name__ == '__main__':
    app.run(debug=True)
