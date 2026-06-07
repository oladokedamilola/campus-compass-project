import os
from flask import Blueprint, render_template
from flask_login import login_required, current_user

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
@login_required
def index():
    """Full-screen map page (authenticated users only)"""
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    return render_template('map.html', google_maps_api_key=google_maps_api_key)

@map_bp.route('/public')
def public_map():
    """Public map page - accessible without login"""
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    # If user is authenticated, redirect to the authenticated map
    if current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for('map.index'))
    
    return render_template('map_guest.html', google_maps_api_key=google_maps_api_key)