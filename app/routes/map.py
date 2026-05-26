import os
from flask import Blueprint, render_template
from flask_login import login_required

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
@login_required
def index():
    """Full-screen map page"""
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    return render_template('map.html', google_maps_api_key=google_maps_api_key)