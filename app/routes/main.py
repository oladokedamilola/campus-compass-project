"""
Campus Compass - Public Routes (Home, etc.)
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
import json
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page - shows appropriate content based on auth status"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/locations')
@login_required
def locations():
    """Display all campus locations in grid view (authenticated users only)"""
    return render_template('locations.html')

@main_bp.route('/locations/public')
def public_locations():
    """Public locations page - accessible without login"""
    # If user is authenticated, redirect to the authenticated locations page
    if current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for('main.locations'))
    
    return render_template('locations_guest.html')

@main_bp.route('/api/buildings')
def api_buildings():
    """API endpoint to get all buildings data (public access)"""
    try:
        data_path = os.path.join('static', 'data', 'campus_data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500