from dash import html, dcc, callback, Input, Output
import dash
from dash.dependencies import Input, Output, State
import math

# Add formula documentation
FREQUENCY_FORMULAS = {
    'Fundamental (fr)': {
        'formula': 'fr = Input value (Hz)',
        'description': 'Inner ring rotational frequency'
    },
    'Cage relative to outer (fc/o)': {
        'formula': 'fc/o = fr/2 × [1 - (d/D)×cos(α)]',
        'description': 'Fundamental train frequency relative to outer raceway'
    },
    'Cage relative to inner (fc/i)': {
        'formula': 'fc/i = fr/2 × [1 + (d/D)×cos(α)]',
        'description': 'Fundamental train frequency relative to inner raceway'
    },
    'Ball pass outer (fb/o)': {
        'formula': 'fb/o = Z × fc/o',
        'description': 'Ball pass frequency of outer raceway'
    },
    'Ball pass inner (fb/i)': {
        'formula': 'fb/i = Z × fc/i',
        'description': 'Ball pass frequency of inner raceway'
    },
    'Rolling element spin (fb)': {
        'formula': 'fb = (D/2d) × fr × [1 - (d/D × cos(α))²]',
        'description': 'Rolling element spin frequency'
    }
}

def create_calculator_layout():
    return html.Div([
        html.H2("Bearing Frequency Calculator", style={'textAlign': 'center'}),
        
        # Input parameters with tooltips
        html.Div([
            html.Div([
                html.Label([
                    "Pitch Circle Diameter (D) [mm]:",
                    html.Span(" ℹ️", title="Distance between the centers of opposite balls", 
                             style={'cursor': 'help'})
                ], style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='input-D',
                    type='number',
                    value=28.5,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label([
                    "Roller Element Diameter (d) [mm]:",
                    html.Span(" ℹ️", title="Diameter of the rolling elements (balls)", 
                             style={'cursor': 'help'})
                ], style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='input-d',
                    type='number',
                    value=6.0,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label([
                    "Inner Ring Rotational Frequency (fr) [Hz]:",
                    html.Span(" ℹ️", title="Rotation speed of the inner ring", 
                             style={'cursor': 'help'})
                ], style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='input-fr',
                    type='number',
                    value=16.8,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label([
                    "Contact Angle (α) [degrees]:",
                    html.Span(" ℹ️", title="Angle between the ball and the radial plane", 
                             style={'cursor': 'help'})
                ], style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='input-alpha',
                    type='number',
                    value=23.4,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                
                html.Label([
                    "Number of Rolling Elements (Z):",
                    html.Span(" ℹ️", title="Total number of balls in the bearing", 
                             style={'cursor': 'help'})
                ], style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='input-Z',
                    type='number',
                    value=10,
                    style={'width': '100%', 'marginBottom': '20px'}
                ),
            ], style={'width': '40%', 'display': 'inline-block', 'padding': '20px'}),
            
            # Results table with formulas
            html.Div([
                html.Table([
                    html.Tr([
                        html.Th("Frequency Type"), 
                        html.Th("Formula"),
                        html.Th("Value (Hz)")
                    ]),
                    *[
                        html.Tr([
                            html.Td(name),
                            html.Td(
                                FREQUENCY_FORMULAS[name]['formula'], 
                                title=FREQUENCY_FORMULAS[name]['description'],
                                style={'cursor': 'help', 'fontFamily': 'monospace'}
                            ),
                            html.Td(id=f'freq-{name.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "")}')
                        ])
                        for name in FREQUENCY_FORMULAS.keys()
                    ]
                ], style={
                    'width': '100%',
                    'borderCollapse': 'collapse',
                    'border': '1px solid black',
                    'margin': '20px 0'
                })
            ], style={'width': '55%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'})
        ], style={'textAlign': 'center'})
    ])

def register_calculator_callbacks(app):
    @app.callback(
        [Output(f'freq-{name.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "")}', 'children')
         for name in FREQUENCY_FORMULAS.keys()] +
        [Output('bearing-frequencies-store', 'data')],
        [Input('input-D', 'value'),
         Input('input-d', 'value'),
         Input('input-fr', 'value'),
         Input('input-alpha', 'value'),
         Input('input-Z', 'value')]
    )
    def update_frequencies(D, d, fr, alpha, Z):
        if None in [D, d, fr, alpha, Z]:
            return ['N/A'] * (len(FREQUENCY_FORMULAS) + 1)
        
        # Convert angle to radians
        alpha_rad = math.radians(alpha)
        cos_alpha = math.cos(alpha_rad)
        
        # Calculate frequencies using formulas
        fco = fr/2 * (1 - d/D * cos_alpha)
        fci = fr/2 * (1 + d/D * cos_alpha)
        fbo = Z * fco
        fbi = Z * fci
        fb = D/(2*d) * fr * (1 - (d/D * cos_alpha)**2)
        
        # Create frequencies dictionary
        frequencies = {
            'Fundamental (fr)': fr,
            'Cage relative to outer (fc/o)': fco,
            'Cage relative to inner (fc/i)': fci,
            'Ball pass outer (fb/o)': fbo,
            'Ball pass inner (fb/i)': fbi,
            'Rolling element spin (fb)': fb
        }
        
        # Return formatted values for display AND the raw dictionary for storage
        return [f"{frequencies[name]:.3f}" for name in FREQUENCY_FORMULAS.keys()] + [frequencies]