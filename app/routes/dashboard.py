# app/routes/dashboard.py
"""
Campus Compass - Dashboard Routes
User dashboard with role-based views
"""

from flask import Blueprint, render_template, jsonify, request, url_for
from flask_login import login_required, current_user, logout_user
from app import db
from app.models import User, SavedLocation
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename

dashboard_bp = Blueprint('dashboard', __name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== ROLE DECORATORS ====================

def student_required(f):
    """Decorator to restrict access to student users only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        if not current_user.is_student():
            return jsonify({'success': False, 'message': 'Student access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to restrict access to admin users only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        if not current_user.is_admin():
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== PAGE ROUTES ====================

@dashboard_bp.route('/')
@login_required
def index():
    """User dashboard - different view based on role"""
    return render_template('dashboard.html', user=current_user)


@dashboard_bp.route('/favorites')
@login_required
def favorites():
    """View saved favorites"""
    return render_template('favorites.html', user=current_user)


@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)


# ==================== API ROUTES ====================

@dashboard_bp.route('/stats')
@login_required
def get_stats():
    """Get dashboard statistics (for AJAX)"""
    stats = {
        'user': {
            'name': current_user.full_name,
            'matric_number': current_user.matric_number,  # Changed from email
            'type': current_user.user_type,
            'member_since': current_user.created_at.strftime('%B %Y') if current_user.created_at else 'Recently'
        },
        'saved_count': SavedLocation.query.filter_by(user_id=current_user.id).count(),
        'user_count': User.query.filter_by(is_active=True).count()
    }
    
    # Add role-specific stats
    if current_user.is_admin():
        total_users = User.query.count()
        total_students = User.query.filter_by(user_type='student').count()
        total_admins = User.query.filter_by(user_type='admin').count()
        total_saved = SavedLocation.query.count()
        
        stats['admin_stats'] = {
            'total_users': total_users,
            'total_students': total_students,
            'total_admins': total_admins,
            'total_saved_locations': total_saved
        }
    
    return jsonify(stats)


@dashboard_bp.route('/favorites/list')
@login_required
def get_favorites():
    """Get user's saved locations as JSON"""
    favorites = SavedLocation.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'success': True,
        'favorites': [fav.to_dict() for fav in favorites]
    })


@dashboard_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    """Add a location to user's favorites"""
    try:
        # Log the raw request data
        print("=" * 50)
        print("REQUEST HEADERS:", dict(request.headers))
        print("REQUEST DATA:", request.get_data(as_text=True))
        
        data = request.get_json()
        print("PARSED JSON:", data)
        
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        place_name = data.get('place_name', '').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        description = data.get('description', '')
        building_type = data.get('building_type', '')
        
        print(f"Extracted - place_name: '{place_name}', lat: {latitude}, lng: {longitude}")
        
        # Validation
        if not place_name:
            return jsonify({'success': False, 'message': 'Place name is required'}), 400
        
        if latitude is None or longitude is None:
            return jsonify({'success': False, 'message': f'Coordinates are required. Got lat={latitude}, lng={longitude}'}), 400
        
        # Convert to float if needed
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Invalid coordinate format'}), 400
        
        # Check if already saved by place_name
        existing = SavedLocation.query.filter_by(
            user_id=current_user.id,
            place_name=place_name
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': f'{place_name} is already in your favorites'}), 400
        
        # Create new favorite
        new_favorite = SavedLocation(
            user_id=current_user.id,
            place_name=place_name,
            latitude=latitude,
            longitude=longitude,
            description=description,
            building_type=building_type
        )
        
        db.session.add(new_favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✓ {place_name} added to favorites',
            'favorite': new_favorite.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Add favorite error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@dashboard_bp.route('/favorites/remove/<int:fav_id>', methods=['DELETE'])
@login_required
def remove_favorite(fav_id):
    """Remove a location from user's favorites"""
    try:
        favorite = SavedLocation.query.filter_by(id=fav_id, user_id=current_user.id).first()
        
        if not favorite:
            return jsonify({'success': False, 'message': 'Favorite not found'}), 404
        
        place_name = favorite.place_name
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✓ {place_name} removed from favorites'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to remove favorite. Please try again.'}), 500


@dashboard_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile (password only)"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_new_password = data.get('confirm_new_password', '')
        
        # If no new password, just return success
        if not new_password:
            return jsonify({'success': True, 'message': 'No changes made'})
        
        # Validate current password
        if not current_password:
            return jsonify({'success': False, 'message': 'Current password is required'}), 400
        
        if not current_user.check_password(current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400
        
        if new_password != confirm_new_password:
            return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500
    

@dashboard_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    """Soft delete user account"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        
        if not current_user.check_password(password):
            return jsonify({'success': False, 'message': 'Incorrect password'}), 400
        
        # Soft delete - deactivate account
        current_user.is_active = False
        db.session.commit()
        
        # Delete user's favorites
        SavedLocation.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        # Logout user
        logout_user()
        
        return jsonify({'success': True, 'message': 'Your account has been deleted'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete account'}), 500
    
    
@dashboard_bp.route('/profile/check-password', methods=['POST'])
@login_required
def check_password():
    """Check if new password is different from current password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'is_same': False})
        
        # Check if new password is the same as current
        is_same = current_user.check_password(new_password)
        
        return jsonify({
            'is_same': is_same
        })
    except Exception as e:
        print(f"Check password error: {str(e)}")
        return jsonify({'is_same': False}), 500