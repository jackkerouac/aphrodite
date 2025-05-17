from app import create_app
import os
import sys
import logging
from waitress import serve

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/app/data/aphrodite.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    # Print startup information
    print("=" * 50)
    print("Aphrodite Web Wrapper")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print("Starting server on http://0.0.0.0:5000")
    print("=" * 50)
    
    # Log directories and permissions
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Data directory exists: {os.path.exists('/app/data')}")
    logger.info(f"Data directory permissions: {oct(os.stat('/app/data').st_mode)}")
    logger.info(f"Data directory is writable: {os.access('/app/data', os.W_OK)}")
    
    # Use Waitress instead of Flask's development server
    logger.info("Starting Waitress production server...")
    serve(app, host='0.0.0.0', port=5000)
