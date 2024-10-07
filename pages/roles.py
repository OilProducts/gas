# pages/roles.py
import json

import dash
from dash import html, dcc, Input, Output, State, callback

dash.register_page(__name__)

def load_role_definitions():
    with open('pages/roles.json', 'r') as f:
        role_definitions = json.load(f)
    return role_definitions

def save_role_definitions(role_definitions):
    with open('roles.json', 'w') as f:
        json.dump(role_definitions, f, indent=2)

role_definitions = load_role_definitions()
roles = list(role_definitions.keys())

layout = html.Div([
    html.H3('Edit Roles'),
    dcc.Dropdown(
        id='role-selector',
        options=[{'label': role, 'value': role} for role in roles],
        placeholder='Select a role to edit',
    ),
    html.Br(),
    html.Div(id='role-editor'),
    html.Br(),
    html.Button('Save Changes', id='save-button', n_clicks=0),
    html.Div(id='save-confirmation', style={'color': 'green'}),
])

@callback(
    Output('role-editor', 'children'),
    [Input('role-selector', 'value')]
)
def display_role_editor(selected_role):
    if selected_role:
        role_definitions = load_role_definitions()
        system_message = role_definitions[selected_role]['system_message']
        return [
            html.H3(f'Editing Role: {selected_role}'),
            dcc.Textarea(
                id='system-message-input',
                value=system_message,
                style={'width': '100%', 'height': '300px'}
            ),
        ]
    else:
        return ''

@callback(
    Output('save-confirmation', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('role-selector', 'value'),
     State('system-message-input', 'value')],
    prevent_initial_call=True
)
def save_role_definition(n_clicks, selected_role, system_message):
    if n_clicks > 0 and selected_role and system_message:
        role_definitions = load_role_definitions()
        role_definitions[selected_role]['system_message'] = system_message
        save_role_definitions(role_definitions)
        return 'Changes saved successfully.'
    else:
        return ''
