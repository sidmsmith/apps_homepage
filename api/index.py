from flask import Flask, jsonify, send_from_directory, request
import os
import requests
import urllib3
from datetime import datetime, timezone

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

USAGE_INGEST_URL = os.getenv("MANHATTAN_USAGE_INGEST_URL", "").strip()
USAGE_INGEST_SECRET = os.getenv("MANHATTAN_USAGE_INGEST_SECRET", "").strip()
APP_NAME = "apps-homepage"
APP_VERSION = "1.3.0"

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
        'id': 'inspection',
        'name': 'Inspection',
        'url': 'https://inspection-manh.vercel.app',
        'vercel_project': 'inspection',
        'description': 'Inspection app with updates and photos',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'facility_addresses',
        'name': 'Facility Address Update',
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
        'name': 'Appointment Date Update',
        'url': 'https://update-appt.vercel.app',
        'vercel_project': 'update_appt',
        'description': 'Tool for updating appointment dates and managing appointment schedules',
        'version': None,
        'lastUpdated': None
    },
    {
        'id': 'item_generator_gallery',
        'name': 'Item Generator Gallery',
        'url': 'https://itemgenerator-gallery.vercel.app',
        'vercel_project': 'item_generator_gallery',
        'description': 'Generate product items, download images, and bulk import to Manhattan WMS',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'proofofdelivery',
        'name': 'Proof of Delivery',
        'url': 'https://proofofdelivery.vercel.app',
        'vercel_project': 'proofofdelivery',
        'description': 'Capture delivery confirmations and proof-of-delivery details',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'cycle_count',
        'name': 'Cycle Count Import',
        'url': 'https://cyclecount.vercel.app/',
        'vercel_project': 'cycle_count',
        'description': 'Import and manage cycle count data',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'work_order_update',
        'name': 'Work Order Update',
        'url': 'https://work-order-update.vercel.app',
        'vercel_project': 'work_order_update',
        'description': 'Update Work Order item descriptions from the Item Master',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'dispatch',
        'name': 'Dispatch',
        'url': 'https://dispatch-manh.vercel.app',
        'vercel_project': 'dispatch',
        'description': 'Trip filtering and driver self-assignment for Manhattan TMS',
        'version': None,
        'lastUpdated': None,
        'under_development': True
    },
    {
        'id': 'dispatch_request',
        'name': 'Manual Dispatch Request',
        'url': 'https://dispatch-request.vercel.app',
        'vercel_project': 'dispatch_request',
        'description': 'Create Transportation Orders and dispatch trips manually',
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
    },
    {
        'id': 'driver_pickup',
        'name': 'Driver Pickup',
        'url': 'https://driver-pickup.vercel.app',
        'vercel_project': 'driver_pickup',
        'description': 'Signature capture for truck drivers during pickup',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'item_update',
        'name': 'Item Update',
        'url': 'https://item-update.vercel.app',
        'vercel_project': 'item_update',
        'description': 'Update Item Master fields and item image',
        'version': None,
        'lastUpdated': None,
        'under_development': True
    },
    {
        'id': 'flowthrough',
        'name': 'Flowthrough',
        'url': 'https://flowthrough.vercel.app',
        'vercel_project': 'flowthrough',
        'description': 'ASN-driven replenishment allocation — preview algorithms and create facility orders',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'item_generator',
        'name': 'Item Copy',
        'url': 'https://item-copy.vercel.app',
        'vercel_project': 'item-generator',
        'description': 'Copy an existing Item Master record and create a new item with updated ID and description',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'supplierenablement',
        'name': 'Supplier Enablement',
        'url': 'https://supplierenablement.vercel.app',
        'vercel_project': 'supplierenablement',
        'description': 'Create ASNs from POs and generate LPNs against Manhattan WMS',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'receivingworkbench',
        'name': 'Receiving Workbench',
        'url': 'https://receivingworkbench.vercel.app',
        'vercel_project': 'receivingworkbench',
        'description': 'Receive against an ASN from a warehouse dock — full, partial, or all-lines receiving',
        'version': None,
        'lastUpdated': None,
        'under_development': False
    },
    {
        'id': 'vasexecution',
        'name': 'VAS Execution',
        'url': 'https://vasexecution.vercel.app',
        'vercel_project': 'vasexecution',
        'description': 'Look up and complete assigned VAS services on an oLPN',
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

def forward_usage_event(payload):
    """POST usage JSON to Manhattan app usage dashboard ingest (Neon)."""
    if not USAGE_INGEST_URL:
        print("[usage] MANHATTAN_USAGE_INGEST_URL not set; event not recorded")
        return
    headers = {"Content-Type": "application/json"}
    if USAGE_INGEST_SECRET:
        headers["Authorization"] = f"Bearer {USAGE_INGEST_SECRET}"
    try:
        requests.post(USAGE_INGEST_URL, json=payload, headers=headers, timeout=8)
    except Exception as e:
        print(f"[usage] Forward failed: {e}")


@app.route('/api/usage-track', methods=['POST'])
def usage_track():
    """Receive events from frontend and forward to usage ingest."""
    data = request.json
    event_name = data.get('event_name')
    metadata = data.get('metadata', {})
    # Spread metadata first so server fields (app_name, app_version, event_name, timestamp) cannot be overridden by the client.
    payload = {
        **metadata,
        "event_name": event_name,
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    forward_usage_event(payload)
    return jsonify({"success": True})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Serve index.html for SPA"""
    # Don't serve index.html for JavaScript files that don't exist - return 404 instead
    if path.endswith('.js'):
        return jsonify({'error': 'File not found'}), 404
    return send_from_directory(os.path.dirname(os.path.dirname(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

