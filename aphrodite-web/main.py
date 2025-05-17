from app import create_app
import webbrowser
import threading
import time
import os
import sys

app = create_app()

if __name__ == '__main__':
    # Print startup information
    print("=" * 50)
    print("Aphrodite Web Wrapper")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print("Starting server on http://localhost:5000")
    print("=" * 50)
    
    # Start the Flask app with debugging enabled
    app.run(debug=True, host='localhost', port=5000)
