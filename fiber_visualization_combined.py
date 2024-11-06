from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import numpy as np
import pandas as pd
from pathlib import Path
import logging

# Add CSS loading
def load_css():
    css_path = Path(__file__).parent / "templates" / "styles.css"
    with open(css_path, 'r') as f:
        return f.read()

# Convert BEARING_FREQUENCIES from constant to a global variable that can be updated
global_bearing_frequencies = {
    'Fundamental (fr)': 16.8,
    'Cage relative to outer (fc/o)': 6.411,
    'Cage relative to inner (fc/i)': 10.389,
    'Ball pass outer (fb/o)': 64.11,
    'Ball pass inner (fb/i)': 103.89,
    'Rolling element spin (fb)': 33.494
}

# Add this after BEARING_FREQUENCIES definition
FREQUENCY_COLORS = {
    'Fundamental (fr)': '#FF0000',
    'Cage relative to outer (fc/o)': '#00FF00',
    'Cage relative to inner (fc/i)': '#0000FF',
    'Ball pass outer (fb/o)': '#FFA500',
    'Ball pass inner (fb/i)': '#800080',
    'Rolling element spin (fb)': '#008080'
}

# Add to imports
from bearing_calculator import create_calculator_layout, register_calculator_callbacks

class FiberData:
    """Class to handle data for a single fiber"""
    def __init__(self, fiber_name: str, viz_data_dir: Path):
        self.fiber_name = fiber_name
        self.viz_data_dir = viz_data_dir
        self.frequencies = None
        self.timestamps = None
        self.magnitude_matrix = None
        self.load_data()

    def load_data(self) -> None:
        """Load pre-processed shortened visualization data"""
        try:
            # Load timestamps
            timestamp_df = pd.read_parquet(
                self.viz_data_dir / f"{self.fiber_name}_timestamps_short.parquet"
            )
            self.timestamps = pd.to_datetime(timestamp_df['timestamp']).values
            
            # Load frequencies
            self.frequencies = np.load(
                self.viz_data_dir / f"{self.fiber_name}_frequencies_short.npy"
            )
            
            # Load magnitude matrix
            self.magnitude_matrix = np.load(
                self.viz_data_dir / f"{self.fiber_name}_magnitude_matrix_short.npy"
            )
            
            logging.info(f"Loaded shortened data for {self.fiber_name}:")
            logging.info(f"Timestamps: {len(self.timestamps)}")
            logging.info(f"Matrix shape: {self.magnitude_matrix.shape}")
            
        except Exception as e:
            logging.error(f"Error loading data for {self.fiber_name}: {str(e)}")
            raise

class FiberVisualizer:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.project_dir = Path(__file__).parent
        print(self.project_dir)
        self.viz_data_dir = self.project_dir / "shortened_data"
        self.fiber_data_cache = {}

    def create_dashboard(self) -> dash.Dash:
        app = dash.Dash(
            __name__, 
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        
        # Add calculator modal
        calculator_modal = dbc.Modal(
            [
                dbc.ModalHeader("Bearing Frequency Calculator"),
                dbc.ModalBody(create_calculator_layout()),
                dbc.ModalFooter([
                    dbc.Button(
                        "Update Main View", 
                        id="update-main", 
                        color="primary", 
                        className="mr-2"
                    ),
                    dbc.Button(
                        "Close", 
                        id="close-calculator", 
                        color="secondary"
                    )
                ]),
            ],
            id="calculator-modal",
            size="lg",
            is_open=False,
        )
        
        # Add calculator button to bearing frequency table
        bearing_table = html.Div([
            html.Table([
                html.Tr([
                    html.Th("Bearing Frequencies", colSpan=2),
                ], style={'backgroundColor': '#e9ecef', 'textAlign': 'center'}),
                *[
                    html.Tr([
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
                        html.Td(f"{freq:.2f} Hz", 
                               style={'fontSize': '11px', 'padding': '4px', 'textAlign': 'right'})
                    ]) 
                    for name, freq in global_bearing_frequencies.items()
                ]
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'marginTop': '20px',
                'border': '1px solid #dee2e6'
            }, id="bearing-frequency-table"),
            
            dbc.Button(
                "Calculate Frequencies",
                id='open-calculator',
                color="primary",
                size="sm",
                className="mt-2",
                style={'width': '100%'}
            )
        ], style={'width': '200px', 'padding': '10px'})

        # Add magnitude range sliders for each fiber
        magnitude_controls = []
        for group in [1, 2]:
            for fiber in range(1, 6):
                magnitude_controls.append(
                    html.Div([
                        html.Label(f'Fiber {group}_{fiber}:'),
                        dcc.RangeSlider(
                            id=f'magnitude-range-{group}-{fiber}',
                            min=0,
                            max=5,
                            step=0.05,
                            value=[0,0.5],
                            marks={i: str(i) for i in range(-100, 1, 20)}
                        )
                    ])
                )
        
        # Add modal to layout
        app.layout = html.Div([
            # Add a Store component to maintain state
            dcc.Store(id='bearing-frequencies-store', data=global_bearing_frequencies),
            
            html.H1("Combined Fiber Spectrograms", 
                    style={'textAlign': 'center', 'fontSize': '24px', 'margin': '10px'}),
            
            # Flex container
            html.Div([
                # Left sidebar with controls
                html.Div([
                    bearing_table,
                    html.Div(magnitude_controls, style={'marginTop': '20px'})
                ], style={'width': '250px', 'padding': '10px'}),
                
                calculator_modal,
                
                # Plot container
                html.Div([
                    dcc.Graph(
                        id='combined-spectrograms',
                        style={'height': '90vh'}
                    ),
                ], style={'width': 'calc(100% - 250px)', 'padding': '10px'})
                
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
            })
        ])
        
        # Register calculator callbacks
        register_calculator_callbacks(app)
        
        # Add modal control callbacks
        @app.callback(
            Output("calculator-modal", "is_open"),
            [Input("open-calculator", "n_clicks"), 
             Input("close-calculator", "n_clicks")],
            [State("calculator-modal", "is_open")],
        )
        def toggle_modal(n1, n2, is_open):
            if n1 or n2:
                return not is_open
            return is_open

        # Add new callback to update bearing frequencies table
        @app.callback(
            Output("bearing-frequency-table", "children"),
            [Input("bearing-frequencies-store", "data")]
        )
        def update_bearing_table(frequencies):
            if not frequencies:
                frequencies = global_bearing_frequencies
            
            return [
                html.Tr([
                    html.Th("Bearing Frequencies", colSpan=2),
                ], style={'backgroundColor': '#e9ecef', 'textAlign': 'center'}),
                *[
                    html.Tr([
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
                        html.Td(f"{freq:.2f} Hz", 
                               style={'fontSize': '11px', 'padding': '4px', 'textAlign': 'right'})
                    ]) 
                    for name, freq in frequencies.items()
                ]
            ]

        @app.callback(
            Output('combined-spectrograms', 'figure'),
            [Input(f'magnitude-range-{group}-{fiber}', 'value') 
             for group in [1, 2] for fiber in range(1, 6)] +
            [Input('bearing-frequencies-store', 'data')]
        )
        def update_spectrograms(*inputs):
            magnitude_ranges = inputs[:-1]  # All inputs except the last one
            frequencies = inputs[-1]  # Last input is the frequencies
            
            if not frequencies:
                frequencies = global_bearing_frequencies
            
            fig = make_subplots(
                rows=2, cols=5,
                subplot_titles=[f'Fiber {group}_{fiber}' 
                              for group in [1, 2] 
                              for fiber in range(1, 6)],
                vertical_spacing=0.2,
                horizontal_spacing=0.05
            )

            idx = 0
            for group in [1, 2]:
                for fiber in range(1, 6):
                    fiber_name = f'fiber_{group}_{fiber}'
                    magnitude_range = magnitude_ranges[idx]
                    row = group
                    col = fiber
                    
                    # Initialize time_strings outside try block
                    time_strings = []
                    
                    try:
                        if fiber_name not in self.fiber_data_cache:
                            self.fiber_data_cache[fiber_name] = FiberData(
                                fiber_name, 
                                self.viz_data_dir
                            )
                        
                        fiber_data = self.fiber_data_cache[fiber_name]
                        time_strings = [pd.Timestamp(t).strftime('%d/%m') 
                                      for t in fiber_data.timestamps if t is not None]
                        
                        # Calculate center position for colorbar
                        subplot_width = 1/5
                        subplot_start = (col - 1) * subplot_width
                        subplot_center = subplot_start + subplot_width/2
                        
                        y_position = 0.57 if row == 1 else -0.05
                        
                        min_val = magnitude_range[0]
                        max_val = magnitude_range[1]
                        
                        fig.add_trace(
                            go.Heatmap(
                                z=fiber_data.magnitude_matrix.T,
                                x=np.arange(len(time_strings)),
                                y=fiber_data.frequencies,
                                colorscale='Viridis',
                                zmin=min_val,
                                zmax=max_val,
                                connectgaps=False,
                                hoverongaps=False,
                                showscale=True,
                                zsmooth='best',
                                xgap=0,
                                ygap=0,
                                customdata=time_strings,
                                hovertemplate='Time: %{customdata}<br>' +
                                            'Frequency: %{y:.1f} Hz<br>' +
                                            'Magnitude: %{z:.2f}<extra></extra>',
                                colorbar=dict(
                                    title=dict(
                                        text="Magnitude",
                                        side='bottom',
                                        font=dict(size=8)
                                    ),
                                    thickness=8,
                                    len=0.15,
                                    x=subplot_center,
                                    y=y_position,
                                    yanchor='top',
                                    xanchor='center',
                                    orientation='h',
                                    tickfont=dict(size=8),
                                    tickangle=0,
                                    ticks='outside',
                                    ticklen=2,
                                    tickwidth=1,
                                    tickcolor='black',
                                    tickmode='array',
                                    tickvals=[min_val, 
                                             (min_val + max_val)/2,
                                             max_val],
                                    ticktext=[f'{min_val:.2f}',
                                            f'{(min_val + max_val)/2:.2f}',
                                            f'{max_val:.2f}'],
                                    xpad=0,
                                    showticklabels=True
                                )
                            ),
                            row=row, col=col
                        )
                        
                        # Update the frequency indicators using the current frequencies
                        for freq_name, freq_value in frequencies.items():
                            fig.add_trace(
                                go.Scatter(
                                    x=[0],
                                    y=[freq_value],
                                    mode='markers',
                                    marker=dict(
                                        color=FREQUENCY_COLORS[freq_name],
                                        size=8,
                                        symbol='circle'
                                    ),
                                    showlegend=False,
                                    hovertemplate=f'{freq_name}: {freq_value:.2f} Hz<extra></extra>'
                                ),
                                row=row,
                                col=col
                            )

                    except Exception as e:
                        print(f"Error loading {fiber_name}: {str(e)}")
                    
                    # Update axes for this subplot
                    if len(time_strings) > 0:  # Only update if we have time data
                        fig.update_xaxes(
                            showticklabels=True,
                            ticktext=time_strings[::len(time_strings)//5],
                            tickvals=np.arange(len(time_strings))[::len(time_strings)//3],
                            tickangle=45,
                            tickfont=dict(size=8),
                            title=None,
                            row=row,
                            col=col
                        )
                    
                    fig.update_yaxes(
                        title_text="Frequency (Hz)" if col == 1 else None,
                        title_font=dict(size=10),
                        tickfont=dict(size=8),
                        row=row,
                        col=col
                    )
                    
                    idx += 1

            # Update layout
            fig.update_layout(
                height=1000,
                showlegend=False,
                margin=dict(t=50, b=100, l=20, r=100),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            return fig

        return app

def main():
    project_dir = Path(__file__).parent.parent
    visualizer = FiberVisualizer(project_dir)
    app = visualizer.create_dashboard()
    app.run_server(debug=True, port=8050)

if __name__ == "__main__":
    main() 