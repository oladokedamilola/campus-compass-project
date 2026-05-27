"""
Campus Compass - Admin Routes
Complete implementation for admin panel
"""

import json
import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, SavedLocation
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Path to campus data JSON file
CAMPUS_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', 'campus_data.json')

def admin_required(f):
    """Decorator to restrict access to admin users only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== PAGE ROUTES ====================

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page"""
    return render_template('admin/dashboard.html')


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users page"""
    return render_template('admin/users.html')


@admin_bp.route('/campus-data')
@login_required
@admin_required
def campus_data():
    """Campus data editor page"""
    return render_template('admin/campus_editor.html')


# ==================== USER MANAGEMENT APIS ====================

@admin_bp.route('/users/list')
@login_required
@admin_required
def list_users():
    """Get all users"""
    users = User.query.all()
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    })


@admin_bp.route('/users/recent')
@login_required
@admin_required
def recent_users():
    """Get recently registered users (last 10)"""
    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    })


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        data = request.get_json()
        print(f"Edit user data received: {data}")  # Debug log
        
        # Update fields
        if 'full_name' in data and data['full_name']:
            user.full_name = data['full_name']
        
        # Update matric_number if provided and not already taken
        if 'matric_number' in data and data['matric_number']:
            matric = data['matric_number'].strip().upper()
            # Check if matric number is taken by another user
            existing = User.query.filter(User.matric_number == matric, User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'message': 'Matric number already in use'}), 400
            user.matric_number = matric
        
        if 'user_type' in data and data['user_type'] in ['student', 'admin']:
            user.user_type = data['user_type']
        
        if 'password' in data and data['password'] and len(data['password']) >= 6:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Edit user error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    


@admin_bp.route('/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (soft delete with option for hard delete)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot delete your own account'}), 400
        
        # Prevent deleting the last admin
        if user.is_admin():
            admin_count = User.query.filter_by(user_type='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Cannot delete the last admin account'}), 400
        
        # Store user info for response message
        user_name = user.full_name
        user_matric = user.matric_number
        
        # Soft delete - deactivate account
        user.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'User {user_name} ({user_matric}) has been deactivated'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete user error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the user'}), 500


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status (enable/disable)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot change your own status'}), 400
        
        # Prevent deactivating the last admin
        if user.is_admin() and user.is_active:
            admin_count = User.query.filter_by(user_type='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Cannot deactivate the last admin account'}), 400
        
        data = request.get_json()
        new_status = data.get('is_active', False)
        
        user.is_active = new_status
        db.session.commit()
        
        status_text = 'activated' if new_status else 'deactivated'
        return jsonify({
            'success': True,
            'message': f'User {user.full_name} has been {status_text}'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Toggle status error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/hard-delete', methods=['DELETE'])
@login_required
@admin_required
def hard_delete_user(user_id):
    """Permanently delete user (hard delete)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot delete your own account'}), 400
        
        # Prevent deleting the last admin
        if user.is_admin():
            admin_count = User.query.filter_by(user_type='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Cannot delete the last admin account'}), 400
        
        user_name = user.full_name
        user_matric = user.matric_number
        
        # Delete user's saved locations first
        SavedLocation.query.filter_by(user_id=user_id).delete()
        
        # Hard delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user_name} ({user_matric}) has been permanently deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Hard delete error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== CAMPUS DATA MANAGEMENT APIS ====================

def load_campus_data():
    """Load campus data from JSON file"""
    try:
        with open(CAMPUS_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'buildings': []}


def save_campus_data(data):
    """Save campus data to JSON file"""
    with open(CAMPUS_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@admin_bp.route('/buildings/list')
@login_required
@admin_required
def list_buildings():
    """Get all campus buildings"""
    data = load_campus_data()
    return jsonify({
        'success': True,
        'buildings': data.get('buildings', [])
    })


@admin_bp.route('/buildings/count')
@login_required
def building_count():
    """Get total building count (accessible to students too)"""
    data = load_campus_data()
    return jsonify({
        'success': True,
        'count': len(data.get('buildings', []))
    })


@admin_bp.route('/buildings/add', methods=['POST'])
@login_required
@admin_required
def add_building():
    """Add a new building"""
    try:
        data = load_campus_data()
        buildings = data.get('buildings', [])
        
        new_building = request.get_json()
        
        # Generate new ID
        max_id = max([b.get('id', 0) for b in buildings]) if buildings else 0
        new_building['id'] = max_id + 1
        
        buildings.append(new_building)
        data['buildings'] = buildings
        save_campus_data(data)
        
        return jsonify({'success': True, 'message': f'{new_building["name"]} added successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/buildings/<int:building_id>/edit', methods=['PUT'])
@login_required
@admin_required
def edit_building(building_id):
    """Edit an existing building"""
    try:
        data = load_campus_data()
        buildings = data.get('buildings', [])
        
        updated_building = request.get_json()
        updated_building['id'] = building_id
        
        found = False
        for i, b in enumerate(buildings):
            if b.get('id') == building_id:
                buildings[i] = updated_building
                found = True
                break
        
        if not found:
            return jsonify({'success': False, 'message': 'Building not found'}), 404
        
        data['buildings'] = buildings
        save_campus_data(data)
        
        return jsonify({'success': True, 'message': f'{updated_building["name"]} updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/buildings/<int:building_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_building(building_id):
    """Delete a building"""
    try:
        data = load_campus_data()
        buildings = data.get('buildings', [])
        
        building_to_delete = None
        for b in buildings:
            if b.get('id') == building_id:
                building_to_delete = b
                break
        
        if not building_to_delete:
            return jsonify({'success': False, 'message': 'Building not found'}), 404
        
        buildings = [b for b in buildings if b.get('id') != building_id]
        data['buildings'] = buildings
        save_campus_data(data)
        
        return jsonify({'success': True, 'message': f'{building_to_delete["name"]} deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@admin_bp.route('/reset-requests')
@login_required
@admin_required
def reset_requests():
    """View password reset requests"""
    from app.models import PasswordResetRequest
    return render_template('admin/reset_requests.html')


@admin_bp.route('/reset-requests/list')
@login_required
@admin_required
def list_reset_requests():
    """Get all password reset requests"""
    from app.models import PasswordResetRequest
    requests = PasswordResetRequest.query.order_by(PasswordResetRequest.created_at.desc()).all()
    return jsonify({
        'success': True,
        'requests': [r.to_dict() for r in requests]
    })


@admin_bp.route('/reset-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_reset_request(request_id):
    """Approve password reset request"""
    from app.models import PasswordResetRequest, User
    try:
        reset_request = PasswordResetRequest.query.get(request_id)
        if not reset_request:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        # Find the user
        user = User.query.filter_by(matric_number=reset_request.matric_number).first()
        
        reset_request.status = 'approved'
        reset_request.processed_at = datetime.utcnow()
        reset_request.processed_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Request approved. User can now reset password.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/reset-requests/<int:request_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_reset_request(request_id):
    """Reject password reset request"""
    from app.models import PasswordResetRequest
    try:
        reset_request = PasswordResetRequest.query.get(request_id)
        if not reset_request:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        reset_request.status = 'rejected'
        reset_request.processed_at = datetime.utcnow()
        reset_request.processed_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Request rejected.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500