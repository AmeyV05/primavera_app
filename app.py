from fiber_visualization_combined import FiberVisualizer
from pathlib import Path

def main():
    project_dir = Path(__file__).parent.parent
    visualizer = FiberVisualizer(project_dir)
    app = visualizer.create_dashboard()
    app.run_server(debug=True, port=8040, host="0.0.0.0")

if __name__ == "__main__":
    main()