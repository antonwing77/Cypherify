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
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
])
app.title = "Cypherify - Educational Cipher Tool"
server = app.server

# Add custom CSS for mobile responsiveness
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            /* Desktop styles - sidebar always visible */
            @media (min-width: 769px) {
                .mobile-sidebar {
                    display: block !important;
                    position: static !important;
                    width: 100% !important;
                    height: auto !important;
                    box-shadow: none !important;
                }
            }
            
            /* Mobile-friendly styles */
            @media (max-width: 768px) {
                .container-fluid {
                    padding: 0.5rem !important;
                }
                .card {
                    margin-bottom: 0.75rem !important;
                }
                .card-body {
                    padding: 0.75rem !important;
                }
                .btn {
                    padding: 0.5rem 0.75rem !important;
                    font-size: 0.9rem !important;
                }
                h1 {
                    font-size: 1.5rem !important;
                }
                h5, h6 {
                    font-size: 1rem !important;
                }
                .accordion-button {
                    padding: 0.5rem 0.75rem !important;
                    font-size: 0.85rem !important;
                }
                textarea {
                    font-size: 0.9rem !important;
                }
                .mobile-sidebar {
                    position: fixed !important;
                    top: 0;
                    left: -100%;
                    width: 80%;
                    height: 100vh;
                    z-index: 1050;
                    background: white;
                    transition: left 0.3s ease;
                    overflow-y: auto;
                    box-shadow: 2px 0 10px rgba(0,0,0,0.2);
                }
                .mobile-sidebar.open {
                    left: 0;
                }
                .mobile-overlay {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 1049;
                }
                .mobile-overlay.active {
                    display: block;
                }
                /* Mobile AI chat fixes */
                #ai-chat-history {
                    height: 50vh !important;
                    max-height: 400px !important;
                    overflow-y: auto !important;
                    -webkit-overflow-scrolling: touch !important;
                }
                /* Ensure sticky positioning doesn't break on mobile */
                .col-md-3 .card {
                    position: relative !important;
                }
            }
            
            /* Touch-friendly buttons */
            .btn-sm {
                min-height: 38px;
                display: flex;
                align-items: center;
                justify-content: flex-start;
            }
            
            /* Smooth scrolling */
            html {
                scroll-behavior: smooth;
            }
            
            /* Animation for chat bubbles */
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes typing {
                0%, 60%, 100% { opacity: 0.3; }
                30% { opacity: 1; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

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
    # Mobile overlay for sidebar
    html.Div(id="mobile-overlay", className="mobile-overlay"),
    
    # Simplified Header with mobile menu button
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button(
                    html.I(className="bi bi-list"),
                    id="mobile-menu-btn",
                    color="primary",
                    className="d-md-none me-2",
                    style={'position': 'fixed', 'top': '10px', 'left': '10px', 'zIndex': '1051'}
                ),
                html.H1("Cypherify", className="text-center mb-1", style={'fontSize': '2rem'}),
            ], className="d-flex align-items-center justify-content-center"),
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
        # Left Sidebar - Responsive
        dbc.Col([
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H6("Ciphers", className="mb-3"),
                            dbc.Button(
                                html.I(className="bi bi-x-lg"),
                                id="mobile-close-btn",
                                color="link",
                                className="d-md-none position-absolute top-0 end-0 m-2 text-dark"
                            )
                        ], style={'position': 'relative'}),
                        
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
            ], id="sidebar-wrapper")
        ], width=12, md=2, className="mobile-sidebar", id="mobile-sidebar"),
        
        # Main content - Responsive
        dbc.Col([
            dcc.Store(id='selected-cipher', data='caesar'),
            
            html.Div([
                html.Div(
                    [
                        # Simplified description card
                        dbc.Card([
                            dbc.CardHeader(cipher.get_name(), className="py-2"),
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
                                    style={'height': '80px', 'fontSize': '0.9rem'},
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
                                        ], width=12, md=6 if param['type'] != 'select' else 12)
                                    ], className="mb-2")
                                    for param in cipher.get_parameters()
                                ]),
                                
                                # Compact buttons - stacked on mobile
                                dbc.Row([
                                    dbc.Col([
                                        dbc.ButtonGroup([
                                            dbc.Button("Encrypt" if key not in ['password_strength', 'auto_detect'] else "Analyze",
                                                id={'type': 'encrypt-btn', 'cipher': key}, 
                                                color="primary", 
                                                className="flex-grow-1",
                                                size="sm"),
                                            dbc.Button("Decrypt",
                                                id={'type': 'decrypt-btn', 'cipher': key}, 
                                                color="success",
                                                className="flex-grow-1",
                                                size="sm",
                                                style={'display': 'none' if key in ['password_strength', 'auto_detect'] else 'inline-block'}),
                                        ], className="w-100 d-flex")
                                    ], width=12)
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
            
        ], width=12, md=7, style={'maxHeight': '90vh', 'overflowY': 'auto'}),
        
        # AI Chat - Collapsible on mobile
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Span([
                            html.I(className="bi bi-robot me-2"),
                            "AI Assistant"
                        ], className="fw-bold"),
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
                                'maxHeight': '500px',
                                'minHeight': '300px',
                                'overflowY': 'auto',
                                'overflowX': 'hidden',
                                'marginBottom': '10px',
                                'padding': '10px',
                                'background': '#f8f9fa',
                                'borderRadius': '6px',
                                'fontSize': '0.85rem',
                                'WebkitOverflowScrolling': 'touch'
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
            ])
        ], width=12, md=3, className="mt-3 mt-md-0")
    ], className="mt-2"),
    
    # Footer with GitHub link
    dbc.Row([
        dbc.Col([
            html.Hr(className="mt-4 mb-3"),
            html.Div([
                html.P([
                    "Made by Anton | ",
                    html.A([
                        html.I(className="bi bi-github me-1"),
                        "View on GitHub"
                    ], 
                    href="https://github.com/antonwing77/cypherify",
                    target="_blank",
                    className="text-decoration-none",
                    style={'color': '#0d6efd'})
                ], className="text-center text-muted small mb-2")
            ])
        ])
    ])
], fluid=True, className="p-2 p-md-3", style={'maxWidth': '1600px'})

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

# Add mobile menu callbacks
@app.callback(
    [Output("mobile-sidebar", "className"),
     Output("mobile-overlay", "className")],
    [Input("mobile-menu-btn", "n_clicks"),
     Input("mobile-close-btn", "n_clicks"),
     Input("mobile-overlay", "n_clicks"),
     Input({'type': 'cipher-btn', 'cipher': ALL}, 'n_clicks')],
    [State("mobile-sidebar", "className")],
    prevent_initial_call=True
)
def toggle_mobile_menu(open_clicks, close_clicks, overlay_clicks, cipher_clicks, current_class):
    if ctx.triggered_id == "mobile-menu-btn":
        return "mobile-sidebar open", "mobile-overlay active"
    else:
        # Close on any other action
        return "mobile-sidebar", "mobile-overlay"
