import dash
from dash import dcc, html, Input, Output, State, ALL, callback_context, ctx
import dash_bootstrap_components as dbc
from ciphers import (
    CaesarCipher, VigenereCipher, AESCipher, RSACipher,
    ROT13Cipher, AffineCipher, A1Z26Cipher, BaconCipher,
    RailFenceCipher, MorseCipher, ReverseCipher, PasswordStrengthCipher,
    AutoDetectCipher
)
from components.visualizations import create_frequency_chart, create_rsa_diagram, create_block_diagram
from ai_teacher import AITeacher

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Cypherify - Educational Cipher Tool"
server = app.server  # Expose the Flask server for deployment

# Initialize AI Teacher
ai_teacher = AITeacher()

# Initialize ciphers - organized by category
CIPHERS = {
    'classical': {
        'caesar': CaesarCipher(),
        'vigenere': VigenereCipher(),
        'rot13': ROT13Cipher(),
        'affine': AffineCipher(),
    },
    'transposition': {
        'railfence': RailFenceCipher(),
        'reverse': ReverseCipher(),
    },
    'substitution': {
        'a1z26': A1Z26Cipher(),
        'bacon': BaconCipher(),
        'morse': MorseCipher(),
    },
    'modern': {
        'aes': AESCipher(),
        'rsa': RSACipher()
    },
    'analysis': {
        'password_strength': PasswordStrengthCipher(),
        'auto_detect': AutoDetectCipher()
    }
}

# Flatten for easy access
ALL_CIPHERS = {}
for category in CIPHERS.values():
    ALL_CIPHERS.update(category)

# Layout
app.layout = dbc.Container([
    # Simplified Header
    dbc.Row([
        dbc.Col([
            html.H1("Cypherify", className="text-center mb-1", style={'fontSize': '2rem'}),
            html.P("Educational Cryptography Tool", 
                   className="text-center text-muted mb-2",
                   style={'fontSize': '0.95rem'}),
            dbc.Alert([
                html.Strong("Educational Purpose Only"),
                " - Not for production use"
            ], color="warning", className="mb-3 py-2", style={'fontSize': '0.85rem'})
        ])
    ]),
    
    dbc.Row([
        # Simplified Left Sidebar with Collapsible Categories
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Ciphers", className="mb-3"),
                    
                    # Classical - Collapsible
                    dbc.Accordion([
                        dbc.AccordionItem([
                            html.Div([
                                dbc.Button(
                                    cipher.get_name(),
                                    id={'type': 'cipher-btn', 'cipher': key},
                                    color="primary" if key == 'caesar' else "light",
                                    outline=key != 'caesar',
                                    className="mb-1 w-100 text-start btn-sm",
                                    size="sm"
                                ) for key, cipher in CIPHERS['classical'].items()
                            ])
                        ], title="Classical Ciphers"),
                        
                        dbc.AccordionItem([
                            html.Div([
                                dbc.Button(
                                    cipher.get_name(),
                                    id={'type': 'cipher-btn', 'cipher': key},
                                    color="light",
                                    outline=True,
                                    className="mb-1 w-100 text-start btn-sm",
                                    size="sm"
                                ) for key, cipher in CIPHERS['transposition'].items()
                            ])
                        ], title="Transposition"),
                        
                        dbc.AccordionItem([
                            html.Div([
                                dbc.Button(
                                    cipher.get_name(),
                                    id={'type': 'cipher-btn', 'cipher': key},
                                    color="light",
                                    outline=True,
                                    className="mb-1 w-100 text-start btn-sm",
                                    size="sm"
                                ) for key, cipher in CIPHERS['substitution'].items()
                            ])
                        ], title="Encoding"),
                        
                        dbc.AccordionItem([
                            html.Div([
                                dbc.Button(
                                    cipher.get_name(),
                                    id={'type': 'cipher-btn', 'cipher': key},
                                    color="light",
                                    outline=True,
                                    className="mb-1 w-100 text-start btn-sm",
                                    size="sm"
                                ) for key, cipher in CIPHERS['modern'].items()
                            ])
                        ], title="Modern Crypto"),
                    ], start_collapsed=False, always_open=True, flush=True),
                    
                    html.Hr(className="my-2"),
                    
                    # Analysis as direct button
                    html.Div([
                        dbc.Button(
                            "PIN/Password Analysis",
                            id={'type': 'cipher-btn', 'cipher': 'password_strength'},
                            color="light",
                            outline=True,
                            className="w-100 text-start btn-sm mb-1",
                            size="sm"
                        ),
                        dbc.Button(
                            "Auto-Detect & Decrypt",
                            id={'type': 'cipher-btn', 'cipher': 'auto_detect'},
                            color="light",
                            outline=True,
                            className="w-100 text-start btn-sm",
                            size="sm"
                        )
                    ])
                ], className="p-2")
            ], style={'position': 'sticky', 'top': '10px'})
        ], width=2, style={'maxHeight': '90vh', 'overflowY': 'auto'}),
        
        # Main content - More spacious
        dbc.Col([
            dcc.Store(id='selected-cipher', data='caesar'),
            
            html.Div([
                html.Div(
                    [
                        # Simplified description card
                        dbc.Card([
                            dbc.CardHeader(cipher.get_name()),
                            dbc.CardBody([
                                dcc.Markdown(cipher.get_description(), className="markdown small"),
                                dbc.Badge(cipher.get_security_warning(), color="danger", className="mt-2")
                            ], className="py-2")
                        ], className="mb-2"),
                        
                        # Compact input section
                        dbc.Card([
                            dbc.CardBody([
                                html.Label("Input Text", className="small fw-bold mb-1"),
                                dbc.Textarea(
                                    id={'type': 'input-text', 'cipher': key},
                                    placeholder="Enter text...",
                                    style={'height': '80px'},
                                    className="mb-2"
                                ),
                                
                                # Compact parameters
                                html.Div([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label(param['label'], className="small fw-bold mb-1"),
                                            dbc.Select(
                                                id={'type': 'param', 'cipher': key, 'name': param['name']},
                                                options=[{'label': opt['label'], 'value': opt['value']} 
                                                        for opt in param['options']],
                                                value=param['default'],
                                                size="sm"
                                            ) if param['type'] == 'select' else
                                            dbc.Input(
                                                id={'type': 'param', 'cipher': key, 'name': param['name']},
                                                type='number' if param['type'] == 'number' else 'text',
                                                value=param['default'],
                                                min=param.get('min', 0) if param['type'] == 'number' else None,
                                                max=param.get('max', 100) if param['type'] == 'number' else None,
                                                size="sm"
                                            ) if param['type'] in ['number', 'text'] else
                                            dbc.Checkbox(
                                                id={'type': 'param', 'cipher': key, 'name': param['name']},
                                                label=param['label'],
                                                value=param['default']
                                            )
                                        ], width=12 if param['type'] == 'select' else 6)
                                    ], className="mb-2")
                                    for param in cipher.get_parameters()
                                ]),
                                
                                # Compact buttons
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button("Encrypt" if key not in ['password_strength', 'auto_detect'] else "Analyze",
                                            id={'type': 'encrypt-btn', 'cipher': key}, 
                                            color="primary", 
                                            className="me-1",
                                            size="sm"),
                                        dbc.Button("Decrypt" if key not in ['password_strength', 'auto_detect'] else "Analyze",
                                            id={'type': 'decrypt-btn', 'cipher': key}, 
                                            color="success",
                                            size="sm",
                                            style={'display': 'none' if key in ['password_strength', 'auto_detect'] else 'inline-block'}),
                                    ])
                                ])
                            ], className="p-2")
                        ], className="mb-2"),
                        
                        # Results
                        html.Div(id={'type': 'results-section', 'cipher': key})
                    ],
                    id={'type': 'cipher-section', 'cipher': key},
                    style={'display': 'block' if key == 'caesar' else 'none'}
                )
                for key, cipher in ALL_CIPHERS.items()
            ])
            
        ], width=7, style={'maxHeight': '90vh', 'overflowY': 'auto'}),
        
        # Minimizable AI Chat
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Span("AI Assistant", className="fw-bold"),
                        html.Div([
                            dbc.Button(
                                html.I(className="bi bi-dash-lg", id="ai-toggle-icon"),
                                id="ai-minimize-btn",
                                color="link",
                                size="sm",
                                className="p-0 text-dark"
                            )
                        ], style={'float': 'right'})
                    ])
                ], className="py-2 px-3"),
                
                dbc.Collapse([
                    dbc.CardBody([
                        # Compact chat area
                        html.Div(
                            id="ai-chat-history",
                            style={
                                'height': '40vh',
                                'overflowY': 'auto',
                                'marginBottom': '10px',
                                'padding': '10px',
                                'background': '#f8f9fa',
                                'borderRadius': '6px',
                                'fontSize': '0.85rem'
                            },
                            children=[
                                html.P("Ask me about cryptography!", 
                                      className="text-muted small text-center mb-0")
                            ] if ai_teacher.enabled else [
                                html.P("API key required", 
                                      className="text-muted small text-center mb-0")
                            ]
                        ),
                        
                        dcc.Store(id='conversation-history', data=[]),
                        
                        # Compact input
                        html.Div([
                            dbc.Textarea(
                                id="ai-question-input",
                                placeholder="Ask a question...",
                                style={'fontSize': '0.85rem'},
                                disabled=not ai_teacher.enabled,
                                rows=2,
                                className="mb-2"
                            ),
                            dbc.Button("Send",
                                id="ask-ai-btn",
                                color="primary",
                                disabled=not ai_teacher.enabled,
                                size="sm",
                                className="w-100"
                            )
                        ], className="input-area")
                    ], className="p-2")
                ], id="ai-chat-collapse", is_open=True)
            ], style={'position': 'sticky', 'top': '10px'})
        ], width=3)
    ], className="mt-2")
], fluid=True, className="p-3", style={'maxWidth': '1600px'})

# Add minimize callback
@app.callback(
    [Output("ai-chat-collapse", "is_open"),
     Output("ai-toggle-icon", "className")],
    Input("ai-minimize-btn", "n_clicks"),
    State("ai-chat-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_ai_chat(n_clicks, is_open):
    if is_open:
        return False, "bi bi-plus-lg"
    return True, "bi bi-dash-lg"

# Callbacks
@app.callback(
    [Output({'type': 'cipher-section', 'cipher': ALL}, 'style'),
     Output({'type': 'cipher-btn', 'cipher': ALL}, 'color'),
     Output({'type': 'cipher-btn', 'cipher': ALL}, 'outline'),
     Output('selected-cipher', 'data')],
    [Input({'type': 'cipher-btn', 'cipher': ALL}, 'n_clicks')],
    [State({'type': 'cipher-btn', 'cipher': ALL}, 'id')],
    prevent_initial_call=False
)
def toggle_cipher_sections(clicks, ids):
    selected = 'caesar'
    
    if ctx.triggered_id:
        # Get the cipher from the triggered button
        selected = ctx.triggered_id['cipher']
    
    # Create display styles
    styles = [{'display': 'block' if id_dict['cipher'] == selected else 'none'} for id_dict in ids]
    
    # Button colors and outlines
    colors = ['primary' if id_dict['cipher'] == selected else 'secondary' for id_dict in ids]
    outlines = [False if id_dict['cipher'] == selected else True for id_dict in ids]
    
    return styles, colors, outlines, selected

@app.callback(
    Output({'type': 'results-section', 'cipher': ALL}, 'children'),
    [Input({'type': 'encrypt-btn', 'cipher': ALL}, 'n_clicks'),
     Input({'type': 'decrypt-btn', 'cipher': ALL}, 'n_clicks')],
    [State({'type': 'input-text', 'cipher': ALL}, 'value'),
     State({'type': 'param', 'cipher': ALL, 'name': ALL}, 'value'),
     State({'type': 'param', 'cipher': ALL, 'name': ALL}, 'id'),
     State({'type': 'encrypt-btn', 'cipher': ALL}, 'id'),
     State({'type': 'decrypt-btn', 'cipher': ALL}, 'id')],
    prevent_initial_call=True
)
def process_cipher(encrypt_clicks, decrypt_clicks, input_texts, param_values, param_ids, 
                   encrypt_btn_ids, decrypt_btn_ids):
    if not ctx.triggered_id:
        return [html.Div() for _ in ALL_CIPHERS]
    
    selected_cipher = ctx.triggered_id['cipher']
    is_encrypt = ctx.triggered_id['type'] == 'encrypt-btn'
    
    cipher_index = list(ALL_CIPHERS.keys()).index(selected_cipher)
    input_text = input_texts[cipher_index] if cipher_index < len(input_texts) else None
    
    if not input_text:
        return [html.Div() for _ in ALL_CIPHERS]
    
    params = {}
    for val, id_dict in zip(param_values, param_ids):
        if id_dict['cipher'] == selected_cipher:
            params[id_dict['name']] = val
    
    cipher = ALL_CIPHERS[selected_cipher]
    try:
        if is_encrypt:
            result = cipher.encrypt(input_text, **params)
        else:
            result = cipher.decrypt(input_text, **params)
    except Exception as e:
        error_result = dbc.Alert(f"Error: {str(e)}", color="danger")
        return [error_result if i == cipher_index else html.Div() for i in range(len(ALL_CIPHERS))]
    
    # Check if this is a brute force result
    is_brute_force = '\n' in result['result'] and 'Shift' in result['result']
    has_brute_force_data = 'brute_force_results' in result
    
    # If brute force and AI enabled, analyze results
    ai_analysis = None
    if has_brute_force_data and ai_teacher.enabled:
        analysis = ai_teacher.analyze_brute_force_results(
            result['brute_force_results'],
            cipher.get_name()
        )
        if analysis['success'] and analysis['best_match']:
            ai_analysis = analysis
    
    components = [
        dbc.Card([
            dbc.CardHeader(html.H5("Result")),
            dbc.CardBody([
                dbc.Textarea(
                    value=result['result'],
                    style={'height': '400px' if is_brute_force else '100px', 'fontFamily': 'monospace'},
                    readonly=True
                ) if is_brute_force else
                dbc.Textarea(
                    value=result['result'],
                    style={'height': '100px'},
                    readonly=True
                )
            ])
        ], className="mb-4")
    ]
    
    # Add AI Analysis card if available
    if ai_analysis:
        best = ai_analysis['best_match']
        confidence_color = {
            'high': 'success',
            'medium': 'warning',
            'low': 'info'
        }.get(ai_analysis['confidence'], 'secondary')
        
        components.insert(0, dbc.Card([
            dbc.CardHeader([
                html.I(className="bi bi-robot me-2"),
                "AI Analysis - Most Likely Correct Result"
            ], className="bg-success text-white"),
            dbc.CardBody([
                dbc.Alert([
                    html.H6(f"🎯 {best['key']}", className="alert-heading"),
                    html.Hr(),
                    html.P(best['text'], style={'fontFamily': 'monospace', 'fontSize': '14px'}),
                    html.Hr(),
                    html.P([
                        html.Strong("Confidence: "),
                        dbc.Badge(ai_analysis['confidence'].upper(), color=confidence_color),
                        html.Br(),
                        html.Strong("Reasoning: "),
                        ai_analysis['explanation']
                    ], className="mb-0 small")
                ], color="success", className="mb-0")
            ])
        ], className="mb-4"))
    
    # Steps
    if result['steps']:
        steps_components = []
        for i, step in enumerate(result['steps']):
            steps_components.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(step['title'], className="text-primary"),
                        html.P(step['description'], className="mb-0", style={'whiteSpace': 'pre-wrap', 'fontFamily': 'monospace' if 'Shift' in step['description'] else 'inherit'})
                    ])
                ], className="mb-2")
            )
        
        components.append(
            dbc.Card([
                dbc.CardHeader(html.H5("Step-by-Step Explanation")),
                dbc.CardBody(steps_components)
            ], className="mb-4")
        )
    
    # Visualizations
    if result.get('visualization_data'):
        viz_data = result['visualization_data']
        
        if viz_data['type'] == 'frequency':
            fig = create_frequency_chart(viz_data['data'])
            components.append(
                dbc.Card([
                    dbc.CardHeader(html.H5("Frequency Analysis")),
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        html.P("Letter frequency can reveal patterns in classical ciphers.",
                               className="text-muted small")
                    ])
                ])
            )
        elif viz_data['type'] == 'rsa_keys':
            fig = create_rsa_diagram(
                viz_data['p'], viz_data['q'], viz_data['n'],
                viz_data['e'], viz_data['d'], viz_data['phi']
            )
            components.append(
                dbc.Card([
                    dbc.CardHeader(html.H5("RSA Key Generation Visualization")),
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        html.P("This shows the mathematical relationship between RSA keys.",
                               className="text-muted small")
                    ])
                ])
            )
        elif viz_data['type'] == 'block_structure':
            fig = create_block_diagram(viz_data['blocks'], viz_data['key_size'])
            components.append(
                dbc.Card([
                    dbc.CardHeader(html.H5("Block Structure Visualization")),
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        html.P("AES processes data in 16-byte blocks.",
                               className="text-muted small")
                    ])
                ])
            )
    
    result_div = html.Div(components)
    
    # Return results only for the active cipher
    return [result_div if i == cipher_index else html.Div() for i in range(len(ALL_CIPHERS))]

# AI Teacher Chat Callback
@app.callback(
    [Output("ai-chat-history", "children"),
     Output("conversation-history", "data"),
     Output("ai-question-input", "value")],
    Input("ask-ai-btn", "n_clicks"),
    [State("ai-question-input", "value"),
     State("selected-cipher", "data"),
     State("ai-chat-history", "children"),
     State("conversation-history", "data")],
    prevent_initial_call=True
)
def handle_ai_chat(n_clicks, question, current_cipher, chat_history, conv_history):
    if not question or not question.strip():
        return chat_history, conv_history or [], question
    
    # Get cipher name for context
    cipher_name = ALL_CIPHERS[current_cipher].get_name() if current_cipher in ALL_CIPHERS else None
    
    # Initialize conversation history if None
    if conv_history is None:
        conv_history = []
    
    # Add user message bubble with modern styling
    user_bubble = html.Div([
        html.Div([
            html.Div([
                html.Small("You", className="text-muted mb-1 d-block", style={'fontSize': '11px'}),
                html.Div(question, style={
                    'whiteSpace': 'pre-wrap',
                    'wordBreak': 'break-word',
                    'fontSize': '14px'
                })
            ], style={
                'backgroundColor': '#667eea',
                'color': 'white',
                'padding': '12px 16px',
                'borderRadius': '18px 18px 4px 18px',
                'maxWidth': '85%',
                'marginLeft': 'auto',
                'boxShadow': '0 2px 4px rgba(102, 126, 234, 0.3)',
                'animation': 'slideInRight 0.3s ease-out'
            })
        ], style={'marginBottom': '12px', 'textAlign': 'right'})
    ])
    
    # Add to chat history display
    new_chat_history = list(chat_history) + [user_bubble]
    
    # Add typing indicator with animation
    typing_bubble = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("●", className="typing-dot", style={
                        'animation': 'typing 1.4s infinite',
                        'animationDelay': '0s',
                        'fontSize': '8px',
                        'marginRight': '3px'
                    }),
                    html.Span("●", className="typing-dot", style={
                        'animation': 'typing 1.4s infinite',
                        'animationDelay': '0.2s',
                        'fontSize': '8px',
                        'marginRight': '3px'
                    }),
                    html.Span("●", className="typing-dot", style={
                        'animation': 'typing 1.4s infinite',
                        'animationDelay': '0.4s',
                        'fontSize': '8px'
                    })
                ], style={'color': '#999'})
            ], style={
                'backgroundColor': '#f1f3f5',
                'padding': '12px 20px',
                'borderRadius': '18px 18px 18px 4px',
                'maxWidth': '85%',
                'display': 'inline-block',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
            })
        ], style={'marginBottom': '12px', 'animation': 'slideInLeft 0.3s ease-out'})
    ])
    
    # Ask the AI with conversation history
    result = ai_teacher.ask(question, cipher_name, conv_history)
    
    if result['success']:
        # Add AI response to conversation history (for API)
        conv_history.append({"role": "user", "content": question})
        conv_history.append({"role": "assistant", "content": result['response']})
        
        # Keep only last 10 messages in history to avoid token limits
        if len(conv_history) > 10:
            conv_history = conv_history[-10:]
        
        # Add AI response bubble with modern styling
        ai_bubble = html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="bi bi-robot me-2", style={'fontSize': '12px'}),
                        html.Small("AI Teacher", style={'fontSize': '11px'})
                    ], className="text-muted mb-1"),
                    dcc.Markdown(result['response'], className="mb-0", style={
                        'fontSize': '14px',
                        'lineHeight': '1.6'
                    })
                ], style={
                    'backgroundColor': '#f8f9fa',
                    'padding': '12px 16px',
                    'borderRadius': '18px 18px 18px 4px',
                    'maxWidth': '85%',
                    'display': 'inline-block',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef'
                })
            ], style={'marginBottom': '12px', 'animation': 'slideInLeft 0.3s ease-out'})
        ])
        new_chat_history.append(ai_bubble)
    else:
        # Add error message with modern styling
        error_bubble = html.Div([
            html.Div([
                html.Div([
                    html.I(className="bi bi-exclamation-circle me-2"),
                    html.Small("Error", className="text-danger fw-bold")
                ], className="mb-1"),
                html.P(result.get('error', 'Unknown error'), className="mb-0 small")
            ], style={
                'backgroundColor': '#fff5f5',
                'color': '#c53030',
                'padding': '12px 16px',
                'borderRadius': '18px 18px 18px 4px',
                'maxWidth': '85%',
                'display': 'inline-block',
                'border': '1px solid #feb2b2',
                'boxShadow': '0 2px 4px rgba(197, 48, 48, 0.1)'
            })
        ], style={'marginBottom': '12px'})
        new_chat_history.append(error_bubble)
    
    # Clear input and return updated chat
    return new_chat_history, conv_history, ""

if __name__ == '__main__':
    app.run(debug=True)
