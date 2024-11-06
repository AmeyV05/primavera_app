"""UI components for the dashboard"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from constants import BEARING_FREQUENCIES, FREQUENCY_COLORS

def create_bearing_table() -> html.Div:
    """Create the bearing frequencies table"""
    return html.Div([
        html.Table([
            html.Tr([html.Th("Bearing Frequencies", colSpan=2)],
                   style={'backgroundColor': '#e9ecef', 'textAlign': 'center'}),
            *[create_frequency_row(name, freq) 
              for name, freq in BEARING_FREQUENCIES.items()]
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'marginTop': '20px',
            'border': '1px solid #dee2e6'
        }, id="bearing-frequency-table")
    ])

def create_frequency_row(name: str, freq: float) -> html.Tr:
    """Create a single row in the frequency table"""
    return html.Tr([
        html.Td([
            html.Div(style={
                'backgroundColor': FREQUENCY_COLORS[name],
                'width': '12px',
                'height': '12px',
                'borderRadius': '50%',
                'display': 'inline-block',
                'marginRight': '5px'
            }),
            name
        ], style={'fontSize': '11px', 'padding': '4px'}),
        html.Td(
            f"{freq:.2f} Hz",
            style={'fontSize': '11px', 'padding': '4px', 'textAlign': 'right'}
        )
    ])

def create_magnitude_controls() -> html.Div:
    """Create all magnitude range slider controls"""
    controls = []
    for group in [1, 2]:
        for fiber in range(1, 6):
            controls.append(
                html.Div([
                    html.Label(
                        f'Magnitude Range - Fiber {group}_{fiber}',
                        style={'fontSize': '12px'}
                    ),
                    dcc.RangeSlider(
                        id=f'magnitude-range-{group}-{fiber}',
                        min=-100,
                        max=0,
                        step=1,
                        value=[-80, -20],
                        marks={
                            -100: {'label': '-100', 'style': {'fontSize': '10px'}},
                            -80: {'label': '-80', 'style': {'fontSize': '10px'}},
                            -60: {'label': '-60', 'style': {'fontSize': '10px'}},
                            -40: {'label': '-40', 'style': {'fontSize': '10px'}},
                            -20: {'label': '-20', 'style': {'fontSize': '10px'}},
                            0: {'label': '0', 'style': {'fontSize': '10px'}}
                        }
                    )
                ], style={'width': '90%', 'margin': '10px auto'})
            )
    return html.Div(controls, style={'marginTop': '20px'})

def create_calculator_modal() -> dbc.Modal:
    """Create the bearing frequency calculator modal"""
    return dbc.Modal([
        dbc.ModalHeader("Bearing Frequency Calculator"),
        dbc.ModalBody([
            html.Div([
                html.Label("Shaft Speed (RPM)", style={'fontSize': '14px'}),
                dcc.Input(
                    id='shaft-speed-input',
                    type='number',
                    placeholder='Enter shaft speed...',
                    style={'width': '100%', 'marginBottom': '15px'}
                ),
                html.Button(
                    'Calculate',
                    id='calculate-button',
                    style={
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 15px',
                        'borderRadius': '4px',
                        'cursor': 'pointer'
                    }
                ),
                html.Div(id='calculation-results', style={'marginTop': '15px'})
            ])
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-calculator", className="ml-auto")
        )
    ], id="calculator-modal", is_open=False)

# Add other component functions... 