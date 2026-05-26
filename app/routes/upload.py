"""
Campus Compass - Upload Routes
Handle file uploads separately
"""

import os
from flask import Blueprint, request, jsonify, url_for, current_app, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# Configure upload settings
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    """Upload profile image"""
    try:
        print("=" * 50)
        print("UPLOAD PROFILE IMAGE ENDPOINT HIT")
        print(f"User: {current_user.id} - {current_user.full_name}")
        print(f"Request method: {request.method}")
        print(f"Request files: {request.files}")
        
        # Check if file exists
        if 'profile_image' not in request.files:
            print("No profile_image in request.files")
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        file = request.files['profile_image']
        print(f"File: {file.filename}, Type: {file.content_type}")
        
        if file.filename == '':
            print("Empty filename")
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            print(f"Invalid file type: {file.filename}")
            return jsonify({'success': False, 'message': 'Invalid file type. Use JPG, PNG, or GIF'}), 400
        
        # Create upload folder if it doesn't exist
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        print(f"Upload path: {upload_path}")
        
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            print(f"Created upload folder: {upload_path}")
        
        # Generate unique filename
        timestamp = int(datetime.now().timestamp())
        filename = secure_filename(f"{current_user.id}_{timestamp}_{file.filename}")
        filepath = os.path.join(upload_path, filename)
        
        # Save file
        file.save(filepath)
        print(f"File saved to: {filepath}")
        
        # Delete old image if exists
        if current_user.profile_image:
            old_path = os.path.join(upload_path, current_user.profile_image)
            if os.path.exists(old_path):
                os.remove(old_path)
                print(f"Deleted old image: {old_path}")
        
        # Update user record
        current_user.profile_image = filename
        db.session.commit()
        print(f"User {current_user.id} profile_image updated to: {filename}")
        
        image_url = url_for('static', filename=f'uploads/{filename}')
        print(f"Image URL: {image_url}")
        
        return jsonify({
            'success': True,
            'message': 'Profile picture updated successfully',
            'image_url': image_url
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500