from app import create_app
import webbrowser
import threading
import time
import os
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Aphrodite Web Wrapper')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', type=int, default=0, help='Enable debug mode (1=True, 0=False)')
    parser.add_argument('--open-browser', type=int, default=0, help='Open browser automatically (1=True, 0=False)')
    return parser.parse_args()

app = create_app()

if __name__ == '__main__':
    args = parse_args()
    
    # Convert numeric args to boolean
    debug_mode = bool(args.debug)
    open_browser = bool(args.open_browser)
    
    # Print startup information
    print("=" * 50)
    print("Aphrodite Web Wrapper")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Starting server on http://{args.host}:{args.port}")
    if debug_mode:
        print("Debug mode: ENABLED")
    print("=" * 50)
    
    # Open browser if requested
    if open_browser:
        def open_browser_delayed():
            time.sleep(1.5)  # Wait for server to start
            url = f"http://localhost:{args.port}"
            print(f"Opening browser to {url}")
            webbrowser.open(url)
            
        threading.Thread(target=open_browser_delayed).start()
    
    # Start the Flask app
    app.run(debug=debug_mode, host=args.host, port=args.port)
