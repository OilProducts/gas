# pages/agent_templates.py
import json
import os

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/agent_templates")

# File path for agent configurations
CONFIG_FILE = './templates/agents.json'

def load_agent_templates():
    if not os.path.exists(CONFIG_FILE):
        # Create an empty templates file if it doesn't exist
        with open(CONFIG_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    with open(CONFIG_FILE, 'r') as f:
        agent_template_definitions = json.load(f)
    return agent_template_definitions

def save_agent_templates(agent_definitions):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(agent_definitions, f, indent=2)

def get_agents():
    agent_definitions = load_agent_templates()
    agents = list(agent_definitions.keys())
    return agents

layout = dmc.Container([
    dmc.Title('Configure Agents', order=2, mb=20),
    dmc.Group([
        dmc.Select(
            id='agent-template-selector',
            label='Select an agent template to edit',
            data=[],
            placeholder='Select an agent template',
            # style={'width': '220px'},
        ),
        dmc.Button('Add New Agent Template', id='add-agent-template-button', variant='outline'),
        dmc.Button('Delete Agent Template', id='delete-agent-template-button', variant='outline',
                   color='red'),
    ]),
    html.Br(),
    dmc.Container(id='agent-template-editor', fluid=True, px=0),
    html.Br(),
    dmc.Group([
        dmc.Button('Save Changes', id='save-button'),
        dmc.Text(id='save-confirmation'),
    ]),
    # Hidden div to store the agent templates for the dropdown
    dcc.Store(id='agent-templates-store', data=get_agents()),
    # Modal for adding a new agent template
    dmc.Modal(
        title="Add New Agent Template",
        id="add-agent-template-modal",
        centered=True,
        children=[
            dmc.TextInput(
                id='new-agent-template-name',
                label='Role Name',
                placeholder='Enter the new agent template name',
            ),
            dmc.Textarea(
                id='new-agent-template-system-message',
                label='System Message',
                placeholder='Enter the system prompt for the new agent template',
                autosize=True,
                minRows=10,
                maxRows=10,
            ),
            dmc.Group([
                dmc.Button('Add Role', id='confirm-add-agent-template', variant='outline'),
                dmc.Button('Cancel', id='cancel-add-agent-template', variant='outline'),
            ], mt=20),
        ],
    ),
    # Modal for confirming agent template deletion
    dmc.Modal(
        title="Delete Role",
        id="delete-agent-template-modal",
        centered=True,
        children=[
            dmc.Text("Are you sure you want to delete this agent template? This action cannot be "
                     "undone."),
            dmc.Group([
                dmc.Button('Delete', id='confirm-delete-agent-template', color='red'),
                dmc.Button('Cancel', id='cancel-delete-agent-template', variant='outline'),
            ], mt=20),
        ],
    ),
])

# Update the agent template selector options
@callback(
    Output('agent-template-selector', 'data'),
    [Input('agent-templates-store', 'data')]
)
def update_agent_template_selector(agent_templates):
    return [{'label': agent_template, 'value': agent_template} for agent_template in agent_templates]

# Display the agent template editor when an agent template is selected
@callback(
    Output('agent-template-editor', 'children'),
    [Input('agent-template-selector', 'value')],
    prevent_initial_call=True
)
def display_agent_template_editor(selected_agent_template):
    if selected_agent_template:
        agent_template_definitions = load_agent_templates()
        agent_template_data = agent_template_definitions.get(selected_agent_template, {})
        system_message = agent_template_data.get('system_message', '')
        tools = agent_template_data.get('tools', [])
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
                placeholder='Select tools available to this agent template',
            ),
        ]
    else:
        raise PreventUpdate

# Save agent template definition
@callback(
    Output('save-confirmation', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('agent-template-selector', 'value'),
     State('system-message-input', 'value'),
     State('tools-input', 'value')],
    prevent_initial_call=True
)
def save_agent_template_definition(n_clicks, selected_agent_template, system_message, tools):
    if n_clicks > 0 and selected_agent_template:
        agent_template_definitions = load_agent_templates()
        agent_template_definitions[selected_agent_template] = {
            'system_message': system_message,
            'tools': tools,
        }
        save_agent_templates(agent_template_definitions)
        return 'Changes saved successfully.'
    else:
        return ''

# Open the add-agent-template modal
@callback(
    Output('add-agent-template-modal', 'opened'),
    [Input('add-agent-template-button', 'n_clicks'),
     Input('confirm-add-agent-template', 'n_clicks'),
     Input('cancel-add-agent-template', 'n_clicks')],
    [State('add-agent-template-modal', 'opened')],
    prevent_initial_call=True
)
def toggle_add_agent_template_modal(add_click, confirm_click, cancel_click, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'add-agent-template-button':
            return True
        else:
            return False
    return is_open

# Confirm adding a new agent template
@callback(
    Output('agent-templates-store', 'data'),
    Output('agent-template-selector', 'value'),
    Output('new-agent-template-name', 'value'),
    Output('new-agent-template-system-message', 'value'),
    [Input('confirm-add-agent-template', 'n_clicks')],
    [State('new-agent-template-name', 'value'),
     State('new-agent-template-system-message', 'value'),
     State('agent-templates-store', 'data')],
    prevent_initial_call=True
)
def add_new_agent_template(n_clicks, new_agent_template_name, new_system_message, agent_templates):
    if n_clicks and new_agent_template_name:
        agent_template_definitions = load_agent_templates()
        agent_template_definitions[new_agent_template_name] = {
            'system_message': new_system_message or '',
            'tools': [],
        }
        save_agent_templates(agent_template_definitions)
        agent_templates.append(new_agent_template_name)
        return agent_templates, new_agent_template_name, '', ''
    else:
        raise PreventUpdate

# Open the delete-agent-template modal
@callback(
    Output('delete-agent-template-modal', 'opened'),
    [Input('delete-agent-template-button', 'n_clicks'),
     Input('confirm-delete-agent-template', 'n_clicks'),
     Input('cancel-delete-agent-template', 'n_clicks')],
    [State('delete-agent-template-modal', 'opened')],
    prevent_initial_call=True
)
def toggle_delete_agent_template_modal(delete_click, confirm_click, cancel_click, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'delete-agent-template-button':
            return True
        else:
            return False
    return is_open

# Confirm deleting an agent template
@callback(
    Output('agent-templates-store', 'data', allow_duplicate=True),
    Output('agent-template-selector', 'value', allow_duplicate=True),
    Output('save-confirmation', 'children', allow_duplicate=True),
    [Input('confirm-delete-agent-template', 'n_clicks')],
    [State('agent-template-selector', 'value'),
     State('agent-templates-store', 'data')],
    prevent_initial_call=True
)
def delete_agent_template(n_clicks, selected_agent_template, agent_templates):
    if n_clicks and selected_agent_template:
        agent_template_definitions = load_agent_templates()
        if selected_agent_template in agent_template_definitions:
            del agent_template_definitions[selected_agent_template]
            save_agent_templates(agent_template_definitions)
            agent_templates.remove(selected_agent_template)
            return agent_templates, None, f'Role "{selected_agent_template}" has been deleted.'
    else:
        raise PreventUpdate
