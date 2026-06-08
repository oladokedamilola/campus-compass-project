"""
Campus Compass - Public Routes (Home, etc.)
"""

from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
import json
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page - redirect authenticated users to dashboard"""
    # If user is logged in, redirect to dashboard instead of showing landing page
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('dashboard.index'))
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page - accessible to everyone, but redirect logged-in users to about page within dashboard?"""
    # Keep about page public, but optionally redirect authenticated users
    # For better UX, we can keep this public or redirect
    # Let's keep it public but add a "Go to Dashboard" link
    return render_template('about.html')

@main_bp.route('/locations')
@login_required
def locations():
    """Display all campus locations in grid view (authenticated users only)"""
    return render_template('locations.html')

@main_bp.route('/locations/public')
def public_locations():
    """Public locations page - redirect authenticated users to authenticated version"""
    # If user is authenticated, redirect to the authenticated locations page
    if current_user.is_authenticated:
        return redirect(url_for('main.locations'))
    
    return render_template('locations_guest.html')

@main_bp.route('/api/buildings')
def api_buildings():
    """API endpoint to get all buildings data - public access"""
    try:
        data_path = os.path.join('static', 'data', 'campus_data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/offline')
def offline():
    """Offline fallback page"""
    return render_template('offline.html'), 503