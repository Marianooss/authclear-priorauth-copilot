#!/usr/bin/env python
"""
Run AuthClear Web UI
Simple HTTP server to serve the web interface
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve from web_ui directory"""

    def __init__(self, *args, **kwargs):
        # Change to web_ui directory before initializing
        web_ui_dir = Path(__file__).parent / 'web_ui'
        super().__init__(*args, directory=str(web_ui_dir), **kwargs)

    def end_headers(self):
        # Add CORS headers to allow requests from the frontend
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def log_message(self, format, *args):
        # Cleaner logging
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    # Verify web_ui directory exists
    web_ui_path = Path(__file__).parent / 'web_ui'
    if not web_ui_path.exists():
        print(f"[ERROR] web_ui directory not found at: {web_ui_path}")
        print("        Please make sure web_ui/index.html exists")
        exit(1)

    if not (web_ui_path / 'index.html').exists():
        print(f"[ERROR] index.html not found in web_ui directory")
        print(f"        Expected: {web_ui_path / 'index.html'}")
        exit(1)

    print("=" * 80)
    print("  AuthClear Web UI Server")
    print("=" * 80)
    print()
    print(f"  Starting server on port {PORT}...")
    print(f"  Serving files from: {web_ui_path}")
    print(f"  Open your browser to: http://localhost:{PORT}")
    print()
    print("  NOTE: The UI works standalone (no backend needed)")
    print("        For full functionality, run: python run_a2a_agent.py")
    print()
    print("  Press Ctrl+C to stop the server")
    print("=" * 80)
    print()

    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            # Open browser automatically after a short delay
            import threading
            def open_browser():
                import time
                time.sleep(1)
                webbrowser.open(f'http://localhost:{PORT}')

            threading.Thread(target=open_browser, daemon=True).start()

            print(f"[OK] Server running at http://localhost:{PORT}")
            print()
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[Shutting down server...]")
    except OSError as e:
        if e.errno == 10048:  # Port already in use on Windows
            print(f"\n[ERROR] Port {PORT} is already in use.")
            print("        Try closing other applications or change the PORT variable.")
        else:
            print(f"\n[ERROR] {e}")
