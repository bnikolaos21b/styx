#!/usr/bin/env python3
"""STYX — Simple HTTP Server for Conversation Log Viewer"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# Change to the directory where this script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create server on port 8892
HOST = '0.0.0.0'
PORT = 8892

httpd = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
print(f"STYX serving on http://{HOST}:{PORT}")
httpd.serve_forever()
