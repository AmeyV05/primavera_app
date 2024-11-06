"""Constants used throughout the application"""

# Bearing frequencies and their corresponding colors
BEARING_FREQUENCIES = {
    'Fundamental (fr)': 16.8,
    'Cage relative to outer (fc/o)': 6.411,
    'Cage relative to inner (fc/i)': 10.389,
    'Ball pass outer (fb/o)': 64.11,
    'Ball pass inner (fb/i)': 103.89,
    'Rolling element spin (fb)': 33.494
}

FREQUENCY_COLORS = {
    'Fundamental (fr)': '#FF0000',
    'Cage relative to outer (fc/o)': '#00FF00',
    'Cage relative to inner (fc/i)': '#0000FF',
    'Ball pass outer (fb/o)': '#FFA500',
    'Ball pass inner (fb/i)': '#800080',
    'Rolling element spin (fb)': '#008080'
}

# Dashboard styling
STYLES = {
    'HEADER': {
        'textAlign': 'center',
        'fontSize': '24px',
        'margin': '10px'
    },
    'MAIN_CONTAINER': {
        'display': 'flex',
        'flexDirection': 'row'
    },
    'SIDEBAR': {
        'width': '250px',
        'padding': '10px'
    },
    'PLOT_CONTAINER': {
        'width': 'calc(100% - 250px)',
        'padding': '10px'
    }
} 