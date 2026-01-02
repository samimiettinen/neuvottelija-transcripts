import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000
DIRECTORY = "public"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server():
    # Check if public directory exists
    if not os.path.exists(DIRECTORY):
        print(f"Error: Directory '{DIRECTORY}' not found.")
        return

    # Check if firebase_config.json exists in public
    if not os.path.exists("public/firebase_config.json"):
        print("WARNING: public/firebase_config.json not found!")
        print("Please copy public/firebase_config.example.json to public/firebase_config.json and add your credentials.")
        print("The app will not work correctly without it.")
    
    # Allow passing port as argument
    port = PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        print("Press Ctrl+C to stop")
        
        # Open browser automatically
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()
