#!/usr/bin/env python
"""
AuthClear Web Server - Serves Web UI + FHIR files
"""
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from pathlib import Path
import sys
import webbrowser
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

BASE_DIR = Path(__file__).parent
WEB_UI_DIR = BASE_DIR / 'web_ui'
FHIR_DIR = BASE_DIR / 'shared' / 'fhir' / 'synthetic_patients'

@app.route('/')
def index():
    """Serve index.html"""
    print(f"[DEBUG] Serving index.html from {WEB_UI_DIR}")
    return send_from_directory(WEB_UI_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from web_ui"""
    print(f"[DEBUG] Serving static file: {path}")
    try:
        return send_from_directory(WEB_UI_DIR, path)
    except Exception as e:
        print(f"[ERROR] File not found: {path} - {e}")
        return jsonify({"error": "File not found"}), 404

@app.route('/fhir/<path:filename>')
def serve_fhir(filename):
    """Serve FHIR files"""
    try:
        return send_from_directory(FHIR_DIR, filename)
    except:
        return jsonify({"error": f"FHIR file not found: {filename}"}), 404

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "authclear-web-ui",
        "web_ui_dir": str(WEB_UI_DIR),
        "fhir_dir": str(FHIR_DIR)
    })

def open_browser():
    """Open browser after server starts"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:3000')

if __name__ == '__main__':
    # Verify directories exist
    if not WEB_UI_DIR.exists():
        print(f"[ERROR] Web UI directory not found: {WEB_UI_DIR}")
        sys.exit(1)

    if not FHIR_DIR.exists():
        print(f"[ERROR] FHIR directory not found: {FHIR_DIR}")
        sys.exit(1)

    print("=" * 80)
    print("  AuthClear Web Server")
    print("=" * 80)
    print()
    print(f"  Web UI: http://localhost:3000")
    print(f"  Serving from: {WEB_UI_DIR}")
    print(f"  FHIR files: {FHIR_DIR}")
    print()
    print("  IMPORTANT:")
    print("  1. MCP Server should be running on port 8001")
    print("  2. A2A Agent should be running on port 8000")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask server
    try:
        app.run(host='0.0.0.0', port=3000, debug=False)
    except KeyboardInterrupt:
        print("\n\n[Shutting down...]")
