"""
Simple preview server for apps_homepage
This serves the static files and provides a mock API endpoint for apps
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import os

class AppsHomepageHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        # Handle API endpoints first
        if self.path == '/api/apps':
            # Return mock app data
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            mock_apps = [
                {
                    'id': 'item_generator_gallery',
                    'name': 'Item Generator',
                    'url': 'https://itemgenerator-gallery.vercel.app',
                    'description': 'Generate product items, download images, and bulk import to Manhattan WMS',
                    'version': 'v0.0.5',
                    'lastUpdated': '2024-01-01',
                    'under_development': True
                },
                {
                    'id': 'appt_app',
                    'name': 'Check In Kiosk',
                    'url': 'https://checkinkiosk.vercel.app',
                    'description': 'Check-in kiosk application for appointment management',
                    'version': 'v1.0.0',
                    'lastUpdated': '2024-01-01'
                }
            ]
            
            self.wfile.write(json.dumps(mock_apps).encode())
            return
        
        # Normalize root path to index.html
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        
        # Serve static files (including index.html, manhlogo.png, etc.)
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress default logging or customize it
        pass

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AppsHomepageHandler)
    print(f'Preview server running at http://localhost:{port}/')
    print('Press Ctrl+C to stop')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped')
        httpd.shutdown()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)

