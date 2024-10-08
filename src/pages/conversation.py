# import json
# import datetime
#
# import dash
# from dash import dcc, html, callback
# from dash.dependencies import Input, Output, State
# import dash_mantine_components as dmc
#
# print(__name__)
#
# #from .events import Event
# from utils.agent_load import load_agents
#
# dash.register_page(__name__)
#
# # Global variable to store the event
# event = None
#
# # Participants (adjust as needed)
# participants = ['Product Owner', 'Scrum Master', 'Lead Developer', 'Developer One', 'Developer Two']
#
#
# # Model settings
# model_name = 'llama3.1:8b-instruct-q8_0'
# model_endpoint = 'http://127.0.0.1:11434'
#
#
# def load_conversation_history():
#     try:
#         with open('conversation_history.json', 'r') as f:
#             conversation_history = json.load(f)
#     except FileNotFoundError:
#         conversation_history = {}
#     return conversation_history
#
#
# conversation_history = load_conversation_history()
#
# # Get the list of participants
# # participants = sorted(set(entry['sender'] for entry in conversation_history))
#
# layout = dmc.Container(
#     dmc.Stack([
#         dmc.Group([
#             dmc.Title('Conversation Threads', order=4)
#         ],
#             style={'position': 'sticky', 'justify': 'top', 'width': '100%', 'height': '50px'}
#         ),
#
#         dmc.Flex([
#             dmc.Stack(id='conversation-thread',
#                       style={'overflow-y': 'scroll', 'max-height': 'calc(100vh - 200px)'}),
#         ]),
#
#         dmc.Group([
#             dmc.Button('Start Event', id='start-event-button', n_clicks=0),
#             dmc.Textarea(id='user-input', placeholder='Enter your message here',
#                          minRows=3,
#                          maxRows=3,
#                          w='60%',
#                          ),
#             dmc.Button('Submit', id='submit-input-button', n_clicks=0,
#                        style={'justify': 'right'}), ],
#             style={'margin-top': 'auto', 'position': 'sticky', 'bottom': '0', 'width': '100%',
#                    'grow': True}
#         ),
#
#         dcc.Interval(
#             id='interval-component',
#             interval=100,  # Update every 5 seconds
#             n_intervals=0
#         ),
#     ], style={'min-height': 'calc(100vh - 25px)'}))
#
#
# # 'max-height': 'calc(100vh - 50px)',
# # 'justify': 'flex-end'})
#
# def generate_conversation_entry(entry):
#     sender = entry['sender']
#     message = entry.get('message')
#     internal_thought = entry.get('internal_thought', 'No thoughts recorded')
#     decision = entry.get('decision')
#
#     if message:
#         message_div = \
#             dmc.Popover([
#                 dmc.PopoverTarget(
#                     dmc.Paper(
#                         [dcc.Markdown(message), ],
#                         radius='lg',
#                         p='sm',
#                         shadow='xs',
#                         withBorder=True,
#                     )
#                 ),
#                 dmc.PopoverDropdown(dcc.Markdown(internal_thought), )
#             ], width='600', position='bottom-start'
#             )
#         return message_div
#     else:
#         # Build a similar div for when the agent decides not to respond but grayed out.
#         message_div = \
#             dmc.Popover([
#                 dmc.PopoverTarget(
#                     dmc.Paper(
#                         [html.Span(f"{sender} decided not to respond.", style={'color': 'grey'})],
#                         radius='lg',
#                         p='sm',
#                         shadow='xs',
#                         withBorder=True,
#                     )
#                 ),
#                 dmc.PopoverDropdown(dcc.Markdown(internal_thought))
#             ], width='600', position='bottom-start'
#             )
#         return message_div
#
#
# def format_conversation(conversation_history):  # , selected_participant):
#     formatted_conversation = []
#     for entry in conversation_history:
#         formatted_conversation.append(generate_conversation_entry(entry))
#
#     return formatted_conversation
#
#
# # @callback(
# #     Output('conversation-thread', 'children'),
# #     Input('participant-selector', 'value'),
# #     prevent_initial_call=True
# # )
# # def update_conversation(selected_participant):
# #     conversation_history = load_conversation_history()
# #     conversation = format_conversation(conversation_history, selected_participant)
# #     return conversation
#
#
# @callback(
#     Output('conversation-thread', 'children', allow_duplicate=True),
#     Input('start-event-button', 'n_clicks'),
#     prevent_initial_call=True
# )
# def start_event(n_clicks):
#     global event
#     if n_clicks > 0 and event is None:
#         # Initialize participants
#         scrum_master = roles.ScrumMaster(model_name, model_endpoint=model_endpoint)
#         product_owner = roles.ProductOwner(model_name, is_human=True)
#         developer_one = roles.Developer(model_name, model_endpoint=model_endpoint,
#                                         role='Developer One')
#         developer_two = roles.Developer(model_name, model_endpoint=model_endpoint,
#                                         role='Developer Two')
#         lead_developer = roles.LeadDeveloper(model_name, model_endpoint=model_endpoint)
#
#         # Create the Event
#         event = Event([product_owner, scrum_master, lead_developer, developer_one, developer_two])
#
#         # Initialize conversation history
#         event.conversation_history = []
#
#         return [html.Div('Event started.')]
#     elif event is not None:
#         return [html.Div('Event already started.')]
#     else:
#         return []
#
#
# @callback(
#     Output('user-input', 'value'),
#     Output('conversation-thread', 'children', allow_duplicate=True),
#     Input('submit-input-button', 'n_clicks'),
#     [State('user-input', 'value')],
#     # State('participant-selector', 'value')],
#     prevent_initial_call=True
# )
# def handle_user_input(n_clicks, user_input):  # , selected_participant):
#     global event
#     if n_clicks > 0 and event is not None and user_input:
#         # Assume the first participant is the human Product Owner
#         participant = event.participants[0]
#         # Add the user's input to the conversation history
#         event.conversation_history.append({
#             'sender': participant.role,
#             'message': user_input,
#             'internal_thought': None,
#             'decision': True,
#             'timestamp': datetime.datetime.now().isoformat(),
#         })
#
#         # Process agent turns
#         for agent in event.participants[1:]:
#             context = event.get_combined_history()
#             should_respond, thought_process = agent.should_respond(context)
#             entry = {
#                 'sender': agent.role,
#                 'internal_thought': thought_process,
#                 'decision': should_respond,
#                 'message': None,
#                 'timestamp': datetime.datetime.now().isoformat(),
#             }
#             if should_respond:
#                 message = agent.generate_response(context)
#                 entry = {
#                     'sender': agent.role,
#                     'internal_thought': thought_process,
#                     'decision': should_respond,
#                     'message': message,
#                     'timestamp': datetime.datetime.now().isoformat(),
#                 }
#             event.conversation_history.append(entry)
#
#         # Update the conversation thread
#         conversation = format_conversation(event.conversation_history)  # , selected_participant)
#         # Clear the input field
#         return '', conversation
#     else:
#         if event:
#             conversation = format_conversation(
#                 event.conversation_history)  # , selected_participant)
#         else:
#             conversation = []
#         return user_input, conversation
#
#
# @callback(
#     Output('conversation-thread', 'children', allow_duplicate=True),
#     Input('interval-component', 'n_intervals'),
#     # Input('participant-selector', 'value')],
#     prevent_initial_call=True
# )
# def update_conversation(n_intervals):  # , selected_participant):
#     global event
#     if event:
#         conversation = format_conversation(event.conversation_history)
#         return conversation
#     else:
#         return []
