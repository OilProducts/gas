# pages/roles.py
import json
import os

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

# File path for agent configurations
CONFIG_FILE = './config/agents.json'

def load_role_definitions():
    if not os.path.exists(CONFIG_FILE):
        # Create an empty config file if it doesn't exist
        with open(CONFIG_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    with open(CONFIG_FILE, 'r') as f:
        role_definitions = json.load(f)
    return role_definitions

def save_role_definitions(role_definitions):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(role_definitions, f, indent=2)

def get_roles():
    role_definitions = load_role_definitions()
    roles = list(role_definitions.keys())
    return roles

layout = dmc.Container([
    dmc.Title('Configure Agents', order=2, mb=20),
    dmc.Group([
        dmc.Select(
            id='role-selector',
            label='Select a role to edit',
            data=[],
            placeholder='Select a role',
            style={'width': '200px'},
        ),
        dmc.Button('Add New Role', id='add-role-button', variant='outline'),
        dmc.Button('Delete Role', id='delete-role-button', variant='outline', color='red'),
    ]),
    html.Br(),
    dmc.Container(id='role-editor', fluid=True, px=0),
    html.Br(),
    dmc.Group([
        dmc.Button('Save Changes', id='save-button'),
        dmc.Text(id='save-confirmation'),
    ]),
    # Hidden div to store the roles for the dropdown
    dcc.Store(id='roles-store', data=get_roles()),
    # Modal for adding a new role
    dmc.Modal(
        title="Add New Role",
        id="add-role-modal",
        centered=True,
        children=[
            dmc.TextInput(
                id='new-role-name',
                label='Role Name',
                placeholder='Enter the new role name',
            ),
            dmc.Textarea(
                id='new-role-system-message',
                label='System Message',
                placeholder='Enter the system prompt for the new role',
                autosize=True,
                minRows=10,
                maxRows=10,
            ),
            dmc.Group([
                dmc.Button('Add Role', id='confirm-add-role', variant='outline'),
                dmc.Button('Cancel', id='cancel-add-role', variant='outline'),
            ], mt=20),
        ],
    ),
    # Modal for confirming role deletion
    dmc.Modal(
        title="Delete Role",
        id="delete-role-modal",
        centered=True,
        children=[
            dmc.Text("Are you sure you want to delete this role? This action cannot be undone."),
            dmc.Group([
                dmc.Button('Delete', id='confirm-delete-role', color='red'),
                dmc.Button('Cancel', id='cancel-delete-role', variant='outline'),
            ], mt=20),
        ],
    ),
])

# Update the role selector options
@callback(
    Output('role-selector', 'data'),
    [Input('roles-store', 'data')]
)
def update_role_selector(roles):
    return [{'label': role, 'value': role} for role in roles]

# Display the role editor when a role is selected
@callback(
    Output('role-editor', 'children'),
    [Input('role-selector', 'value')],
    prevent_initial_call=True
)
def display_role_editor(selected_role):
    if selected_role:
        role_definitions = load_role_definitions()
        role_data = role_definitions.get(selected_role, {})
        system_message = role_data.get('system_message', '')
        tools = role_data.get('tools', [])
        return [
            dmc.Textarea(
                id='system-message-input',
                label='System Message',
                value=system_message,
                autosize=True,
                minRows=10,
                maxRows=10,
            ),
            dmc.MultiSelect(
                id='tools-input',
                label='Tools',
                data=['sprint_planner', 'code_executor', 'record_backlog_item'],
                value=tools,
                placeholder='Select tools available to this role',
            ),
        ]
    else:
        raise PreventUpdate

# Save role definition
@callback(
    Output('save-confirmation', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('role-selector', 'value'),
     State('system-message-input', 'value'),
     State('tools-input', 'value')],
    prevent_initial_call=True
)
def save_role_definition(n_clicks, selected_role, system_message, tools):
    if n_clicks > 0 and selected_role:
        role_definitions = load_role_definitions()
        role_definitions[selected_role] = {
            'system_message': system_message,
            'tools': tools,
        }
        save_role_definitions(role_definitions)
        return 'Changes saved successfully.'
    else:
        return ''

# Open the add-role modal
@callback(
    Output('add-role-modal', 'opened'),
    [Input('add-role-button', 'n_clicks'),
     Input('confirm-add-role', 'n_clicks'),
     Input('cancel-add-role', 'n_clicks')],
    [State('add-role-modal', 'opened')],
    prevent_initial_call=True
)
def toggle_add_role_modal(add_click, confirm_click, cancel_click, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'add-role-button':
            return True
        else:
            return False
    return is_open

# Confirm adding a new role
@callback(
    Output('roles-store', 'data'),
    Output('role-selector', 'value'),
    Output('new-role-name', 'value'),
    Output('new-role-system-message', 'value'),
    [Input('confirm-add-role', 'n_clicks')],
    [State('new-role-name', 'value'),
     State('new-role-system-message', 'value'),
     State('roles-store', 'data')],
    prevent_initial_call=True
)
def add_new_role(n_clicks, new_role_name, new_system_message, roles):
    if n_clicks and new_role_name:
        role_definitions = load_role_definitions()
        role_definitions[new_role_name] = {
            'system_message': new_system_message or '',
            'tools': [],
        }
        save_role_definitions(role_definitions)
        roles.append(new_role_name)
        return roles, new_role_name, '', ''
    else:
        raise PreventUpdate

# Open the delete-role modal
@callback(
    Output('delete-role-modal', 'opened'),
    [Input('delete-role-button', 'n_clicks'),
     Input('confirm-delete-role', 'n_clicks'),
     Input('cancel-delete-role', 'n_clicks')],
    [State('delete-role-modal', 'opened')],
    prevent_initial_call=True
)
def toggle_delete_role_modal(delete_click, confirm_click, cancel_click, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'delete-role-button':
            return True
        else:
            return False
    return is_open

# Confirm deleting a role
@callback(
    Output('roles-store', 'data', allow_duplicate=True),
    Output('role-selector', 'value', allow_duplicate=True),
    Output('save-confirmation', 'children', allow_duplicate=True),
    [Input('confirm-delete-role', 'n_clicks')],
    [State('role-selector', 'value'),
     State('roles-store', 'data')],
    prevent_initial_call=True
)
def delete_role(n_clicks, selected_role, roles):
    if n_clicks and selected_role:
        role_definitions = load_role_definitions()
        if selected_role in role_definitions:
            del role_definitions[selected_role]
            save_role_definitions(role_definitions)
            roles.remove(selected_role)
            return roles, None, f'Role "{selected_role}" has been deleted.'
    else:
        raise PreventUpdate
