import http.server
import socketserver
import webbrowser
import os

PORT = 4000

# Define a custom handler to serve files
Handler = http.server.SimpleHTTPRequestHandler

# Change the current working directory to the directory containing index.html
web_dir = "."
os.chdir(web_dir)

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    
    # Open the default web browser
    webbrowser.open(f"http://localhost:{PORT}/index.html")
    
    # Keep the server running until interrupted
    httpd.serve_forever()
