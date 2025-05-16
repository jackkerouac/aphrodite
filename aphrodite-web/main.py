from app import create_app
import webbrowser
import threading
import time
import os

app = create_app()

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Start a thread to open the browser
    threading.Thread(target=open_browser).start()
    
    # Start the Flask app
    app.run(debug=True, host='localhost', port=5000)
