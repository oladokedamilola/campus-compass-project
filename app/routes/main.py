"""
Campus Compass - Public Routes (Home, etc.)
"""

from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page (optional)"""
    return render_template('about.html')

@main_bp.route('/locations')
@login_required
def locations():
    """Display all campus locations in grid view"""
    return render_template('locations.html')
