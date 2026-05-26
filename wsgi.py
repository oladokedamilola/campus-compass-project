"""
Campus Compass - WSGI Entry Point for PythonAnywhere
"""

import sys
import os

# Add your project directory to the path
project_home = '/home/yourusername/campus-compass'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key-change-this'

# Import your Flask app
from app import create_app

# Create the application instance
application = create_app()