from flask import Flask, jsonify, send_from_directory
import os
import requests
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Vercel API Configuration
VERCEL_API_BASE = "https://api.vercel.com"
VERCEL_API_TOKEN = os.getenv("VERCEL_API_TOKEN", "9g83u2AQAW8GeM7TCGDrnFrJ")

# App configurations with metadata
# Note: Versions and last updated dates are fetched dynamically from the apps themselves
APPS_CONFIG = [
    {
        'id': 'appt_app',
        'name': 'Check In Kiosk',
        'url': 'https://checkinkiosk.vercel.app',
        'vercel_project': 'appt_app',
        'description': 'Check-in kiosk application for appointment management',
        'version': None,  # Will be fetched dynamically
        'lastUpdated': None  # Will be fetched dynamically
    },
    {
        'id': 'facility_addresses',
        'name': 'Site Identification Developer',
        'url': 'https://facilityaddresses.vercel.app',
        'vercel_project': 'facility_addresses',
        'description': 'Tool for managing and identifying facility addresses',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'lpn-unlock-app',
        'name': 'LPN Lock / Unlock',
        'url': 'https://lpnlock.vercel.app',
        'vercel_project': 'lpn-unlock-app',
        'description': 'Application for locking and unlocking License Plate Numbers (LPNs)',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'MHE_console',
        'name': 'MHE Console',
        'url': 'https://mhe-console.vercel.app',
        'vercel_project': 'MHE_console',
        'description': 'Material Handling Equipment console for monitoring and managing MHE operations',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'order_generator',
        'name': 'Order Generator',
        'url': 'https://ordergenerator.vercel.app',
        'vercel_project': 'order_generator',
        'description': 'Generate and manage orders with bulk import capabilities and order validation',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'update_appt',
        'name': 'Update Appointment Date',
        'url': 'https://update-appt.vercel.app',
        'vercel_project': 'update_appt',
        'description': 'Tool for updating appointment dates and managing appointment schedules',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'item_generator',
        'name': 'Item Generator',
        'url': 'https://itemmastergenerator.vercel.app',
        'vercel_project': 'item_generator',
        'description': 'Generate product items, download images, and bulk import to Manhattan WMS',
        'version': None,
        'lastUpdated': None,
        'under_development': True
    },
    {
        'id': 'schedule_app',
        'name': 'Appointment Calendar',
        'url': 'https://scheduleappt.vercel.app',
        'vercel_project': 'schedule_app',
        'description': 'Five-day grid for visualizing hourly appointment availability',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    }
]

def fetch_app_version(url):
    """Fetch version from app's HTML page"""
    try:
        response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
        if response.status_code == 200:
            import re
            content = response.text
            
            # Try to find version in title tag (supports v1.0, v1.0.0, etc.)
            title_match = re.search(r'<title>.*?v(\d+\.\d+(?:\.\d+)?).*?</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                version = title_match.group(1)
                # Normalize to three-part version if needed
                parts = version.split('.')
                if len(parts) == 2:
                    version = f"{parts[0]}.{parts[1]}.0"
                return f"v{version}"
            
            # Try to find version in h2 tag
            h2_match = re.search(r'<h2[^>]*>.*?v(\d+\.\d+(?:\.\d+)?).*?</h2>', content, re.IGNORECASE | re.DOTALL)
            if h2_match:
                version = h2_match.group(1)
                # Normalize to three-part version if needed
                parts = version.split('.')
                if len(parts) == 2:
                    version = f"{parts[0]}.{parts[1]}.0"
                return f"v{version}"
    except Exception as e:
        print(f"Error fetching version from {url}: {str(e)}")
    return None

def fetch_deployment_date(project_name):
    """Fetch last deployment date from Vercel API"""
    try:
        headers = {
            'Authorization': f'Bearer {VERCEL_API_TOKEN}'
        }
        
        # First, get the project ID by listing all projects
        projects_url = f"{VERCEL_API_BASE}/v9/projects"
        projects_response = requests.get(projects_url, headers=headers, timeout=10)
        
        if projects_response.status_code == 200:
            projects_data = projects_response.json()
            projects = projects_data.get('projects', [])
            
            # Find project by name (case-insensitive)
            project = None
            for p in projects:
                if p.get('name', '').lower() == project_name.lower():
                    project = p
                    break
            
            if project:
                project_id = project.get('id')
                # Get deployments for this project (most recent production deployment)
                deployments_url = f"{VERCEL_API_BASE}/v6/deployments"
                params = {
                    'projectId': project_id,
                    'limit': 1,
                    'target': 'production',
                    'state': 'READY'
                }
                deployments_response = requests.get(deployments_url, headers=headers, params=params, timeout=10)
                
                if deployments_response.status_code == 200:
                    deployments_data = deployments_response.json()
                    deployments = deployments_data.get('deployments', [])
                    if deployments:
                        created = deployments[0].get('createdAt')
                        if created:
                            # Convert timestamp to date (Vercel timestamps are in milliseconds)
                            dt = datetime.fromtimestamp(created / 1000)
                            return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error fetching deployment date for {project_name}: {str(e)}")
    return None

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Get list of all apps with their information"""
    apps = []
    
    for app_config in APPS_CONFIG:
        # Try to fetch version dynamically
        version = fetch_app_version(app_config['url'])
        
        # Try to fetch deployment date from Vercel API
        last_updated = fetch_deployment_date(app_config.get('vercel_project'))
        if not last_updated:
            last_updated = datetime.now().strftime('%Y-%m-%d')
        
        app_data = {
            'id': app_config['id'],
            'name': app_config['name'],
            'url': app_config['url'],
            'description': app_config['description'],
            'version': version or app_config.get('version'),
            'lastUpdated': last_updated,
            'under_development': app_config.get('under_development', False)
        }
        apps.append(app_data)
    
    return jsonify(apps)

@app.route('/manhlogo.png')
def serve_logo():
    """Serve Manhattan Associates logo"""
    return send_from_directory(os.path.dirname(os.path.dirname(__file__)), 'manhlogo.png')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Serve index.html for SPA"""
    return send_from_directory(os.path.dirname(os.path.dirname(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

