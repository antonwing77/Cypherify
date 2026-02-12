import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH, callback_context, ctx
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
app.title = "Cypherify - Learn Cryptography"
server = app.server

# Icons for each cipher in the sidebar
CIPHER_ICONS = {
    'caesar': 'bi-key-fill',
    'vigenere': 'bi-grid-3x3-gap-fill',
    'rot13': 'bi-arrow-repeat',
    'affine': 'bi-calculator-fill',
    'railfence': 'bi-bar-chart-steps',
    'reverse': 'bi-arrow-left-right',
    'a1z26': 'bi-123',
    'bacon': 'bi-braces',
    'morse': 'bi-broadcast-pin',
    'aes': 'bi-shield-lock-fill',
    'rsa': 'bi-lock-fill',
    'password_strength': 'bi-shield-check',
    'auto_detect': 'bi-search',
}

# Example texts for quick testing
EXAMPLE_TEXTS = {
    'caesar': 'The quick brown fox jumps over the lazy dog',
    'vigenere': 'Attack at dawn, the enemy approaches from the north',
    'rot13': 'Hello World! This is a secret message.',
    'affine': 'Meet me at the park at midnight',
    'railfence': 'We are discovered, flee at once',
    'reverse': 'This message is hidden backwards',
    'a1z26': 'Hello World',
    'bacon': 'Secret',
    'morse': 'SOS We need help',
    'aes': 'Top secret: the treasure is buried under the oak tree',
    'rsa': 'Encrypt this sensitive data',
    'password_strength': '1234',
    'auto_detect': 'Khoor Zruog',
}

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
                .feature-pill {
                    font-size: 0.65rem !important;
                    padding: 0.2rem 0.5rem !important;
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
        <script>
            // Enter key to send AI chat message (Shift+Enter for newline)
            document.addEventListener('keydown', function(e) {
                if (e.target && e.target.id === 'ai-question-input' && e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    var btn = document.getElementById('ask-ai-btn');
                    if (btn && !btn.disabled) btn.click();
                }
            });

            // Copy result to clipboard
            document.addEventListener('click', function(e) {
                var copyBtn = e.target.closest('.copy-result-btn');
                if (copyBtn) {
                    var card = copyBtn.closest('.card');
                    var textarea = card ? card.querySelector('textarea') : null;
                    if (textarea) {
                        navigator.clipboard.writeText(textarea.value).then(function() {
                            var icon = copyBtn.querySelector('i');
                            var span = copyBtn.querySelector('span');
                            if (icon) icon.className = 'bi bi-check-lg me-1';
                            if (span) span.textContent = 'Copied!';
                            setTimeout(function() {
                                if (icon) icon.className = 'bi bi-clipboard me-1';
                                if (span) span.textContent = 'Copy';
                            }, 2000);
                        });
                    }
                }
            });

            // Scroll to top button visibility
            window.addEventListener('scroll', function() {
                var btn = document.getElementById('scroll-top-btn');
                if (btn) {
                    btn.style.display = window.scrollY > 300 ? 'flex' : 'none';
                }
            });

            // Scroll to top action
            document.addEventListener('click', function(e) {
                if (e.target.closest('#scroll-top-btn')) {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        </script>
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


def make_cipher_btn(key, cipher, default_selected='caesar'):
    """Create a sidebar cipher button with an icon."""
    icon_class = CIPHER_ICONS.get(key, 'bi-circle')
    return dbc.Button(
        [html.I(className=f"{icon_class} me-2"), cipher.get_name()],
        id={'type': 'cipher-btn', 'cipher': key},
        color="primary" if key == default_selected else "light",
        outline=key != default_selected,
        className="cipher-nav-btn",
        size="sm"
    )


# Layout
app.layout = dbc.Container([
    # Mobile overlay for sidebar
    html.Div(id="mobile-overlay", className="mobile-overlay"),

    # Scroll to top button
    html.Button(
        html.I(className="bi bi-chevron-up"),
        id="scroll-top-btn",
        className="scroll-top-btn",
        style={'display': 'none'}
    ),

    # Header
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
                html.H1("Cypherify", className="text-center mb-1", style={'fontSize': '2.25rem'}),
            ], className="d-flex align-items-center justify-content-center"),
            html.P("Learn cryptography by doing. Encrypt, decrypt, and explore how ciphers work.",
                   className="text-center hero-subtitle mb-3"),
            # Feature pills
            html.Div([
                html.Span([html.I(className="bi bi-key-fill"), " 13 Ciphers"], className="feature-pill"),
                html.Span([html.I(className="bi bi-lightbulb-fill"), " Step-by-Step"], className="feature-pill"),
                html.Span([html.I(className="bi bi-bar-chart-fill"), " Visualizations"], className="feature-pill"),
                html.Span([html.I(className="bi bi-robot"), " AI Assistant"], className="feature-pill"),
            ], className="text-center mb-3"),
            dbc.Alert([
                html.I(className="bi bi-info-circle-fill me-2"),
                html.Strong("Educational Purpose Only"),
                " - These implementations are for learning, not production use."
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
                            html.H6([
                                html.I(className="bi bi-collection-fill me-2"),
                                "Ciphers"
                            ], className="mb-3 fw-bold"),
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
                                    make_cipher_btn(key, cipher)
                                    for key, cipher in CIPHERS['classical'].items()
                                ])
                            ], title="Classical Ciphers"),

                            dbc.AccordionItem([
                                html.Div([
                                    make_cipher_btn(key, cipher)
                                    for key, cipher in CIPHERS['transposition'].items()
                                ])
                            ], title="Transposition"),

                            dbc.AccordionItem([
                                html.Div([
                                    make_cipher_btn(key, cipher)
                                    for key, cipher in CIPHERS['substitution'].items()
                                ])
                            ], title="Encoding"),

                            dbc.AccordionItem([
                                html.Div([
                                    make_cipher_btn(key, cipher)
                                    for key, cipher in CIPHERS['modern'].items()
                                ])
                            ], title="Modern Crypto"),
                        ], start_collapsed=False, always_open=True, flush=True),

                        html.Hr(className="my-2"),

                        # Analysis tools
                        html.Div([
                            html.Div([
                                html.Small("TOOLS", className="text-muted fw-bold",
                                           style={'fontSize': '0.7rem', 'letterSpacing': '0.05em'}),
                            ], className="mb-2 ms-1"),
                            make_cipher_btn('password_strength', ALL_CIPHERS['password_strength']),
                            make_cipher_btn('auto_detect', ALL_CIPHERS['auto_detect']),
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
                        # Description card
                        dbc.Card([
                            dbc.CardHeader([
                                html.Div([
                                    html.Span([
                                        html.I(className=f"{CIPHER_ICONS.get(key, 'bi-circle')} me-2"),
                                        cipher.get_name()
                                    ], className="fw-bold"),
                                ], className="d-flex align-items-center justify-content-between")
                            ], className="py-2"),
                            dbc.CardBody([
                                dcc.Markdown(cipher.get_description(), className="markdown small"),
                                dbc.Badge([
                                    html.I(className="bi bi-exclamation-triangle-fill me-1"),
                                    cipher.get_security_warning()
                                ], color="danger", className="mt-2")
                            ], className="py-2")
                        ], className="mb-2"),

                        # Input section
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Label("Input Text", className="small fw-bold mb-0"),
                                    dbc.Button(
                                        [html.I(className="bi bi-lightning-fill me-1"),
                                         "Try Example"],
                                        id={'type': 'example-btn', 'cipher': key},
                                        className="example-btn",
                                        size="sm",
                                        outline=True,
                                        color="primary"
                                    ),
                                ], className="d-flex align-items-center justify-content-between mb-1"),
                                dbc.Textarea(
                                    id={'type': 'input-text', 'cipher': key},
                                    placeholder="Enter your text here to encrypt or decrypt...",
                                    style={'height': '80px', 'fontSize': '0.9rem'},
                                    className="mb-0"
                                ),
                                html.Div(
                                    "0 chars",
                                    id={'type': 'char-count', 'cipher': key},
                                    className="char-count mb-2"
                                ),

                                # Parameters
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

                                # Action buttons
                                dbc.Row([
                                    dbc.Col([
                                        dbc.ButtonGroup([
                                            dbc.Button(
                                                [html.I(className="bi bi-lock-fill me-1"),
                                                 "Encrypt" if key not in ['password_strength', 'auto_detect'] else "Analyze"],
                                                id={'type': 'encrypt-btn', 'cipher': key},
                                                color="primary",
                                                className="flex-grow-1",
                                                size="sm"),
                                            dbc.Button(
                                                [html.I(className="bi bi-unlock-fill me-1"),
                                                 "Decrypt"],
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
                        # Chat area
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
                                'background': '#f8fafc',
                                'borderRadius': '8px',
                                'fontSize': '0.85rem',
                                'WebkitOverflowScrolling': 'touch'
                            },
                            children=[
                                html.Div([
                                    html.I(className="bi bi-chat-dots-fill d-block mb-2",
                                           style={'fontSize': '1.5rem', 'color': '#94a3b8'}),
                                    html.P("Ask me anything about cryptography!",
                                          className="text-muted small mb-1"),
                                    html.P("Try: \"How does Caesar cipher work?\"",
                                          className="text-muted small mb-0",
                                          style={'fontStyle': 'italic', 'fontSize': '0.75rem'})
                                ], className="text-center", style={'paddingTop': '40%'})
                            ] if ai_teacher.enabled else [
                                html.Div([
                                    html.I(className="bi bi-key-fill d-block mb-2",
                                           style={'fontSize': '1.5rem', 'color': '#94a3b8'}),
                                    html.P("Set OPENAI_API_KEY to enable the AI assistant.",
                                          className="text-muted small mb-0")
                                ], className="text-center", style={'paddingTop': '40%'})
                            ]
                        ),

                        dcc.Store(id='conversation-history', data=[]),

                        # Input area
                        html.Div([
                            dbc.Textarea(
                                id="ai-question-input",
                                placeholder="Ask a question... (Enter to send, Shift+Enter for newline)",
                                style={'fontSize': '0.85rem'},
                                disabled=not ai_teacher.enabled,
                                rows=2,
                                className="mb-2"
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-send-fill me-1"), "Send"],
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
        ], width=12, md=3, className="mt-3 mt-md-0")
    ], className="mt-2"),

    # Footer
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
                    className="footer-link")
                ], className="text-center text-muted small mb-2")
            ])
        ])
    ])
], fluid=True, className="p-2 p-md-3", style={'maxWidth': '1600px'})


# ── Callbacks ──────────────────────────────────────────────────────────────────

# Character count (clientside for performance)
app.clientside_callback(
    """
    function(value) {
        if (!value) return '0 chars';
        var chars = value.length;
        var words = value.trim().split(/\\s+/).filter(Boolean).length;
        return chars + ' chars \\u00b7 ' + words + ' words';
    }
    """,
    Output({'type': 'char-count', 'cipher': MATCH}, 'children'),
    Input({'type': 'input-text', 'cipher': MATCH}, 'value'),
    prevent_initial_call=True
)

# Fill example text
@app.callback(
    Output({'type': 'input-text', 'cipher': MATCH}, 'value'),
    Input({'type': 'example-btn', 'cipher': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)
def fill_example_text(n_clicks):
    if n_clicks:
        cipher_key = ctx.triggered_id['cipher']
        return EXAMPLE_TEXTS.get(cipher_key, 'Hello World')
    return dash.no_update

# Toggle AI chat panel
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

# Cipher selection
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
        selected = ctx.triggered_id['cipher']

    styles = [{'display': 'block' if id_dict['cipher'] == selected else 'none'} for id_dict in ids]
    colors = ['primary' if id_dict['cipher'] == selected else 'secondary' for id_dict in ids]
    outlines = [False if id_dict['cipher'] == selected else True for id_dict in ids]

    return styles, colors, outlines, selected

# Process cipher encrypt/decrypt
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
        empty_results = [html.Div() for _ in ALL_CIPHERS]
        empty_results[cipher_index] = dbc.Alert(
            [html.I(className="bi bi-info-circle me-2"),
             "Please enter some text to process."],
            color="info", className="mt-2"
        )
        return empty_results

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
        error_result = dbc.Alert(
            [html.I(className="bi bi-exclamation-triangle-fill me-2"),
             f"Error: {str(e)}"],
            color="danger"
        )
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

    # Build result card with copy button
    result_header = html.Div([
        html.Span([
            html.I(className="bi bi-check-circle-fill me-2"),
            "Result"
        ], className="fw-bold"),
        html.Button([
            html.I(className="bi bi-clipboard me-1"),
            html.Span("Copy")
        ], className="btn btn-sm btn-outline-secondary copy-result-btn",
           style={'fontSize': '0.75rem', 'padding': '0.2rem 0.6rem'})
    ], className="d-flex align-items-center justify-content-between")

    components = [
        dbc.Card([
            dbc.CardHeader(result_header),
            dbc.CardBody([
                dbc.Textarea(
                    value=result['result'],
                    style={
                        'height': '400px' if is_brute_force else '100px',
                        'fontFamily': 'monospace'
                    },
                    readonly=True
                )
            ])
        ], className="mb-3 result-card")
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
                "AI Analysis - Most Likely Result"
            ], className="bg-success text-white"),
            dbc.CardBody([
                dbc.Alert([
                    html.H6(best['key'], className="alert-heading fw-bold"),
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
        ], className="mb-3"))

    # Steps
    if result['steps']:
        steps_components = []
        for i, step in enumerate(result['steps']):
            steps_components.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Span(
                                str(i + 1),
                                className="badge bg-primary me-2",
                                style={'fontSize': '0.7rem', 'minWidth': '22px',
                                       'display': 'inline-flex', 'alignItems': 'center',
                                       'justifyContent': 'center'}
                            ),
                            html.Span(step['title'], className="fw-bold small",
                                      style={'color': '#4f46e5'})
                        ], className="mb-2 d-flex align-items-center"),
                        html.P(step['description'], className="mb-0 small",
                               style={
                                   'whiteSpace': 'pre-wrap',
                                   'fontFamily': 'monospace' if 'Shift' in step['description'] else 'inherit',
                                   'lineHeight': '1.6'
                               })
                    ], className="py-2 px-3")
                ], className="step-card")
            )

        components.append(
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="bi bi-list-ol me-2"),
                    html.Span("Step-by-Step Explanation", className="fw-bold")
                ]),
                dbc.CardBody(steps_components)
            ], className="mb-3")
        )

    # Visualizations
    if result.get('visualization_data'):
        viz_data = result['visualization_data']

        if viz_data['type'] == 'frequency':
            fig = create_frequency_chart(viz_data['data'])
            components.append(
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-bar-chart-fill me-2"),
                        html.Span("Frequency Analysis", className="fw-bold")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        html.P("Letter frequency can reveal patterns in classical ciphers.",
                               className="text-muted small mt-2 mb-0")
                    ])
                ], className="mb-3")
            )
        elif viz_data['type'] == 'rsa_keys':
            fig = create_rsa_diagram(
                viz_data['p'], viz_data['q'], viz_data['n'],
                viz_data['e'], viz_data['d'], viz_data['phi']
            )
            components.append(
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-diagram-3-fill me-2"),
                        html.Span("RSA Key Generation", className="fw-bold")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        html.P("This shows the mathematical relationship between RSA keys.",
                               className="text-muted small mt-2 mb-0")
                    ])
                ], className="mb-3")
            )
        elif viz_data['type'] == 'block_structure':
            fig = create_block_diagram(viz_data['blocks'], viz_data['key_size'])
            components.append(
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-grid-3x3-gap-fill me-2"),
                        html.Span("Block Structure", className="fw-bold")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        html.P("AES processes data in 16-byte blocks.",
                               className="text-muted small mt-2 mb-0")
                    ])
                ], className="mb-3")
            )

    result_div = html.Div(components)

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

    cipher_name = ALL_CIPHERS[current_cipher].get_name() if current_cipher in ALL_CIPHERS else None

    if conv_history is None:
        conv_history = []

    # User message bubble
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
                'backgroundColor': '#4f46e5',
                'color': 'white',
                'padding': '12px 16px',
                'borderRadius': '18px 18px 4px 18px',
                'maxWidth': '85%',
                'marginLeft': 'auto',
                'boxShadow': '0 2px 8px rgba(79, 70, 229, 0.25)',
                'animation': 'slideInRight 0.3s ease-out'
            })
        ], style={'marginBottom': '12px', 'textAlign': 'right'})
    ])

    new_chat_history = list(chat_history) + [user_bubble]

    # Ask the AI
    result = ai_teacher.ask(question, cipher_name, conv_history)

    if result['success']:
        conv_history.append({"role": "user", "content": question})
        conv_history.append({"role": "assistant", "content": result['response']})

        if len(conv_history) > 10:
            conv_history = conv_history[-10:]

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
                    'backgroundColor': '#ffffff',
                    'padding': '12px 16px',
                    'borderRadius': '18px 18px 18px 4px',
                    'maxWidth': '85%',
                    'display': 'inline-block',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
                    'border': '1px solid #e2e8f0'
                })
            ], style={'marginBottom': '12px', 'animation': 'slideInLeft 0.3s ease-out'})
        ])
        new_chat_history.append(ai_bubble)
    else:
        error_bubble = html.Div([
            html.Div([
                html.Div([
                    html.I(className="bi bi-exclamation-circle me-2"),
                    html.Small("Error", className="text-danger fw-bold")
                ], className="mb-1"),
                html.P(result.get('error', 'Unknown error'), className="mb-0 small")
            ], style={
                'backgroundColor': '#fef2f2',
                'color': '#991b1b',
                'padding': '12px 16px',
                'borderRadius': '18px 18px 18px 4px',
                'maxWidth': '85%',
                'display': 'inline-block',
                'border': '1px solid #fecaca',
                'boxShadow': '0 2px 4px rgba(153, 27, 27, 0.1)'
            })
        ], style={'marginBottom': '12px'})
        new_chat_history.append(error_bubble)

    return new_chat_history, conv_history, ""

# Mobile menu toggle
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
        return "mobile-sidebar", "mobile-overlay"

    # By Anton Wingeier
