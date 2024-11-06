# Fiber Visualization Dashboard

A web-based dashboard for visualizing fiber spectrogram data using Dash and Plotly.

## Features

- Interactive spectrograms for multiple fiber groups
- Real-time bearing frequency calculations
- Adjustable magnitude ranges for each fiber
- Color-coded bearing frequency indicators

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/fiber-visualization.git
cd fiber-visualization
```

2. Create and activate virtual environment:

For Linux/Mac:
```bash
# Create virtual environment
python -m venv primavera-app

# Activate virtual environment
source primavera-app/bin/activate
```

For Windows:
```bash
# Create virtual environment
python -m venv primavera-app

# Activate virtual environment
primavera-app\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

1. Ensure your virtual environment is activated:
```bash
# Linux/Mac
source primavera-app/bin/activate

# Windows
primavera-app\Scripts\activate
```

2. Start the application:
```bash
python app/main.py
```

3. Open your browser and visit `http://localhost:8002`

## Deployment

This application is configured for deployment with CapRover. To deploy:

1. Ensure you have CapRover CLI installed:
```bash
npm install -g caprover
```

2. Deploy to your CapRover server:
```bash
caprover deploy
```

## Project Structure

- `app/`: Main application directory
  - `visualization/`: Core visualization logic
  - `static/`: CSS and other static files
  - `templates/`: HTML templates
- `Dockerfile`: Container configuration
- `captain-definition`: CapRover deployment configuration

## Data Requirements

The application expects data in the following structure under `app/visualization/prepared_data/`:
- `fiber_X_Y_timestamps.parquet`
- `fiber_X_Y_frequencies.npy`
- `fiber_X_Y_magnitude_matrix.npy`

Where X and Y represent fiber group and number respectively.

## Development

To deactivate the virtual environment when you're done:
```bash
deactivate
```

## Requirements

See `requirements.txt` for a full list of Python dependencies.
