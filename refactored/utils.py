"""Utility functions for data processing and visualization"""
from typing import List, Tuple
import numpy as np
import pandas as pd

def format_time_strings(timestamps: np.ndarray) -> List[str]:
    """Convert timestamps to formatted strings"""
    return [pd.Timestamp(t).strftime('%d/%m') for t in timestamps if t is not None]

def calculate_subplot_position(col: int, row: int, total_cols: int = 5) -> Tuple[float, float]:
    """Calculate subplot position for colorbar placement"""
    subplot_width = 1/total_cols
    subplot_start = (col - 1) * subplot_width
    subplot_center = subplot_start + subplot_width/2
    y_position = 0.57 if row == 1 else -0.05
    
    return subplot_center, y_position

def create_colorbar_dict(min_val: float, max_val: float, 
                        subplot_center: float, y_position: float) -> dict:
    """Create colorbar configuration dictionary"""
    return {
        'title': dict(text="Magnitude", side='bottom', font=dict(size=8)),
        'thickness': 8,
        'len': 0.15,
        'x': subplot_center,
        'y': y_position,
        'yanchor': 'top',
        'xanchor': 'center',
        'orientation': 'h',
        'tickfont': dict(size=8),
        'tickangle': 0,
        'ticks': 'outside',
        'ticklen': 2,
        'tickwidth': 1,
        'tickcolor': 'black',
        'tickmode': 'array',
        'tickvals': [min_val, (min_val + max_val)/2, max_val],
        'ticktext': [f'{min_val:.2f}', f'{(min_val + max_val)/2:.2f}', f'{max_val:.2f}'],
        'xpad': 0,
        'showticklabels': True
    } 