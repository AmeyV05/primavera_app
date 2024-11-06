"""Main visualization module for fiber data"""
from pathlib import Path
import logging
from typing import Dict, Optional
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from constants import BEARING_FREQUENCIES, FREQUENCY_COLORS, STYLES
from utils import format_time_strings, calculate_subplot_position, create_colorbar_dict
from data_handler import DataLoader, FiberData
from components import (
    create_bearing_table,
    create_magnitude_controls,
    create_calculator_modal
)

logger = logging.getLogger(__name__)

class FiberVisualizer:
    """Main visualization controller"""
    def __init__(self, project_dir: Path):
        self.data_loader = DataLoader(project_dir.parent / "prepared_data")
        self.fiber_cache: Dict[str, FiberData] = {}
        self.app = self._initialize_app()

    def _initialize_app(self) -> dash.Dash:
        """Initialize and configure the Dash application"""
        app = dash.Dash(
            __name__,
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        self._create_layout(app)
        self._register_callbacks(app)
        return app

    def _create_layout(self, app: dash.Dash) -> None:
        """Create the dashboard layout"""
        app.layout = html.Div([
            dcc.Store(id='bearing-frequencies-store', data=BEARING_FREQUENCIES),
            html.H1("Combined Fiber Spectrograms", style=STYLES['HEADER']),
            html.Div([
                html.Div([
                    create_bearing_table(),
                    create_magnitude_controls()
                ], style=STYLES['SIDEBAR']),
                create_calculator_modal(),
                html.Div([
                    dcc.Graph(id='combined-spectrograms', style={'height': '90vh'})
                ], style=STYLES['PLOT_CONTAINER'])
            ], style=STYLES['MAIN_CONTAINER'])
        ])

    def _register_callbacks(self, app: dash.Dash) -> None:
        """Register all dashboard callbacks"""
        self._register_modal_callbacks(app)
        self._register_update_callbacks(app)

    def _register_modal_callbacks(self, app: dash.Dash) -> None:
        """Register callbacks for modal interaction"""
        @app.callback(
            Output("calculator-modal", "is_open"),
            [Input("open-calculator", "n_clicks"), 
             Input("close-calculator", "n_clicks")],
            [State("calculator-modal", "is_open")]
        )
        def toggle_modal(n1: Optional[int], n2: Optional[int], is_open: bool) -> bool:
            if n1 or n2:
                return not is_open
            return is_open

    def _register_update_callbacks(self, app: dash.Dash) -> None:
        """Register callbacks for updating visualizations"""
        @app.callback(
            Output('combined-spectrograms', 'figure'),
            [Input(f'magnitude-range-{group}-{fiber}', 'value') 
             for group in [1, 2] for fiber in range(1, 6)] +
            [Input('bearing-frequencies-store', 'data')]
        )
        def update_spectrograms(*inputs) -> go.Figure:
            return self._create_spectrogram_figure(inputs[:-1], inputs[-1])

    def _create_spectrogram_figure(self, magnitude_ranges, frequencies) -> go.Figure:
        """Create the spectrogram figure with all subplots"""
        fig = make_subplots(
            rows=2, cols=5,
            subplot_titles=[f'Fiber {group}_{fiber}' 
                          for group in [1, 2] 
                          for fiber in range(1, 6)],
            vertical_spacing=0.2,
            horizontal_spacing=0.05
        )

        for idx, (group, fiber) in enumerate(
            [(g, f) for g in [1, 2] for f in range(1, 6)]
        ):
            self._add_fiber_subplot(
                fig, group, fiber, 
                magnitude_ranges[idx], 
                frequencies or BEARING_FREQUENCIES
            )

        self._update_figure_layout(fig)
        return fig

    def _add_fiber_subplot(self, fig: go.Figure, group: int, fiber: int, 
                          magnitude_range: list, frequencies: dict) -> None:
        """Add a single fiber subplot to the figure"""
        try:
            fiber_data = self._get_or_create_fiber_data(f'fiber_{group}_{fiber}')
            self._add_heatmap(fig, fiber_data, group, fiber, magnitude_range)
            self._add_frequency_indicators(fig, frequencies, group, fiber)
        except Exception as e:
            logger.error(f"Error adding subplot for fiber_{group}_{fiber}: {str(e)}")

    def _add_heatmap(self, fig: go.Figure, fiber_data: FiberData, 
                     group: int, fiber: int, magnitude_range: list) -> None:
        """Add heatmap for a single fiber"""
        time_strings = format_time_strings(fiber_data.timestamps)
        subplot_center, y_position = calculate_subplot_position(fiber, group)
        
        min_val, max_val = magnitude_range
        colorbar_dict = create_colorbar_dict(min_val, max_val, subplot_center, y_position)
        
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
                colorbar=colorbar_dict
            ),
            row=group,
            col=fiber
        )

    def _add_frequency_indicators(self, fig: go.Figure, frequencies: dict, 
                                group: int, fiber: int) -> None:
        """Add frequency indicators for a single fiber"""
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
                row=group,
                col=fiber
            )

    def _update_figure_layout(self, fig: go.Figure) -> None:
        """Update the layout of the figure"""
        fig.update_layout(
            height=1000,
            showlegend=False,
            margin=dict(t=50, b=100, l=20, r=100),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

    def _get_or_create_fiber_data(self, fiber_name: str) -> FiberData:
        """Get or create fiber data instance"""
        if fiber_name not in self.fiber_cache:
            self.fiber_cache[fiber_name] = FiberData(
                fiber_name,
                self.data_loader,
                time_downsample=10,
                freq_downsample=2
            )
        return self.fiber_cache[fiber_name]

    def run_server(self, debug: bool = False, host: str = '0.0.0.0', 
                  port: int = 8002) -> None:
        """Run the Dash server"""
        self.app.run_server(debug=debug, host=host, port=port)