from app import create_app
import webbrowser
import threading
import time
import os
import sys

app = create_app()

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Print startup information
    print("=" * 50)
    print("Aphrodite Web Wrapper")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print("Starting server on http://localhost:5000")
    print("=" * 50)
    
    # Start a thread to open the browser
    threading.Thread(target=open_browser).start()
    
    # Start the Flask app with debugging enabled
    app.run(debug=True, host='localhost', port=5000)
