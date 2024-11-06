"""Main application entry point"""
import logging
from pathlib import Path
from fiber_visualization import FiberVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Get the project directory (one level up from this file)
        project_dir = Path(__file__).parent
        logger.info(f"Initializing application from directory: {project_dir}")

        # Initialize the visualizer
        visualizer = FiberVisualizer(project_dir)
        logger.info("FiberVisualizer initialized successfully")

        # Run the server
        logger.info("Starting server on port 8002...")
        visualizer.run_server(
            debug=False,
            host='0.0.0.0',
            port=8020
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    main() 