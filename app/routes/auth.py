"""
Campus Compass - Authentication Routes
Matric Number-based Authentication System
Students verify with matric number first, then create password
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, StudentUniversity, PasswordResetRequest
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def is_valid_matric_number(matric):
    """
    Validate matric number format.
    Accepts two formats:
    1. YYYY + 5 digits (total 9 digits) where year is between 2000 and current year
    2. Any 9 random digits (legacy or special format)
    """
    if not matric:
        return False
    
    # Must be exactly 9 digits
    pattern = r'^\d{9}$'
    if not re.match(pattern, matric):
        return False
    
    # Check if it follows the year format (first 4 digits represent a valid year)
    try:
        year = int(matric[:4])
        current_year = datetime.now().year
        # If year is between 2000 and current year, it's valid
        if 2000 <= year <= current_year:
            return True
    except (ValueError, IndexError):
        pass
    
    # If not a valid year format, still accept any 9-digit number
    # This handles legacy matric numbers or special formats
    return True


@auth_bp.route('/verify-matric', methods=['GET'])
def verify_matric_page():
    """Page to verify matric number before registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('verify_matric.html')


@auth_bp.route('/verify-matric', methods=['POST'])
def verify_matric():
    """Verify matric number against university database"""
    try:
        data = request.get_json()
        matric_number = data.get('matric_number', '').strip().upper()
        
        # Validation
        if not matric_number:
            return jsonify({
                'success': False,
                'message': 'Please enter your matric number'
            }), 400
        
        if not is_valid_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must be 9 digits.'
            }), 400
        
        # Check in university database
        student_record = StudentUniversity.query.filter_by(matric_number=matric_number).first()
        
        if not student_record:
            return jsonify({
                'success': False,
                'message': 'Matric number not found in LASU records. Please contact the administration.'
            }), 404
        
        if not student_record.is_active:
            return jsonify({
                'success': False,
                'message': f'Your record is inactive. Status: {student_record.status_note or "Contact administration"}'
            }), 403
        
        # Check if already registered
        existing_user = User.query.filter_by(matric_number=matric_number).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'This matric number is already registered. Please login instead.',
                'redirect': url_for('auth.login_page')
            }), 400
        
        # Store matric number in session for registration
        session['verified_matric'] = matric_number
        session['student_data'] = {
            'full_name': student_record.full_name,
            'email': student_record.email,
            'faculty': student_record.faculty,
            'department': student_record.department,
            'phone': student_record.phone
        }
        
        return jsonify({
            'success': True,
            'message': f'Welcome {student_record.full_name}! Please complete your registration.',
            'redirect': url_for('auth.register_page')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Render login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Process login with matric number and password"""
    try:
        data = request.get_json()
        matric_number = data.get('matric_number', '').strip().upper()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Validation
        if not matric_number or not password:
            return jsonify({
                'success': False,
                'message': 'Please enter both matric number and password'
            }), 400
        
        if not is_valid_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must be 9 digits.'
            }), 400
        
        # Find user by matric number
        user = User.query.filter_by(matric_number=matric_number).first()
        
        # Check credentials
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number or password'
            }), 401
        
        # Check if account is active
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'This account has been deactivated. Please contact an administrator.'
            }), 403
        
        # Login successful
        login_user(user, remember=remember)
        user.update_last_login()
        
        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.full_name.split()[0]}!',
            'redirect': url_for('dashboard.index'),
            'user_type': user.user_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/staff-login', methods=['GET'])
def staff_login_page():
    """Render staff/admin login page"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('dashboard.index'))
    return render_template('staff_login.html')


@auth_bp.route('/staff-login', methods=['POST'])
def staff_login():
    """Process staff/admin login with matric number and password"""
    try:
        data = request.get_json()
        matric_number = data.get('matric_number', '').strip().upper()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Validation
        if not matric_number or not password:
            return jsonify({
                'success': False,
                'message': 'Please enter both matric number and password'
            }), 400
        
        if not is_valid_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must be 9 digits.'
            }), 400
        
        # Find user by matric number
        user = User.query.filter_by(matric_number=matric_number).first()
        
        # Check credentials
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Check if account is active
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'This account has been deactivated. Please contact administration.'
            }), 403
        
        # Check if user is admin/staff
        if not user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Access denied. Staff login only.'
            }), 403
        
        # Login successful
        login_user(user, remember=remember)
        user.update_last_login()
        
        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.full_name.split()[0]}!',
            'redirect': url_for('admin.index'),
            'user_type': user.user_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Render registration page (after matric verification)"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Check if matric was verified
    if 'verified_matric' not in session:
        flash('Please verify your matric number first.', 'warning')
        return redirect(url_for('auth.verify_matric_page'))
    
    return render_template('register.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Complete registration with password creation"""
    try:
        # Check if matric was verified
        if 'verified_matric' not in session:
            return jsonify({
                'success': False,
                'message': 'Please verify your matric number first',
                'redirect': url_for('auth.verify_matric_page')
            }), 401
        
        matric_number = session.get('verified_matric')
        student_data = session.get('student_data', {})
        
        data = request.get_json()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        phone = data.get('phone', '').strip()
        
        # Validation
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        
        # Password validation
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        # Check if user already exists (double-check)
        existing_user = User.query.filter_by(matric_number=matric_number).first()
        if existing_user:
            session.pop('verified_matric', None)
            session.pop('student_data', None)
            return jsonify({
                'success': False,
                'message': 'This matric number is already registered. Please login.',
                'redirect': url_for('auth.login_page')
            }), 400
        
        # Get student record
        student_record = StudentUniversity.query.filter_by(matric_number=matric_number).first()
        if not student_record:
            session.pop('verified_matric', None)
            session.pop('student_data', None)
            return jsonify({
                'success': False,
                'message': 'Student record not found. Please verify again.'
            }), 404
        
        # Create new user account
        new_user = User(
            full_name=student_record.full_name,
            user_type='student',
            matric_number=matric_number,
            faculty=student_record.faculty,
            department=student_record.department,
            phone=phone or student_record.phone
        )
        new_user.set_password(password)
        
        # Mark student as registered in university database
        student_record.has_registered = True
        
        db.session.add(new_user)
        db.session.commit()
        
        # Clear session data
        session.pop('verified_matric', None)
        session.pop('student_data', None)
        
        # Auto-login after registration
        login_user(new_user)
        new_user.update_last_login()
        
        return jsonify({
            'success': True,
            'message': f'Account created successfully! Welcome, {student_record.full_name.split()[0]}!',
            'redirect': url_for('dashboard.index'),
            'user_type': 'student'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration. Please try again.'
        }), 500


@auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """Page to request password reset"""
    return render_template('forgot_password.html')


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Submit password reset request to admin"""
    try:
        data = request.get_json()
        matric_number = data.get('matric_number', '').strip().upper()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        faculty = data.get('faculty', '').strip()
        department = data.get('department', '').strip()
        
        # Validation
        if not all([matric_number, full_name, email, phone, faculty, department]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all fields'
            }), 400
        
        if not is_valid_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must be 9 digits.'
            }), 400
        
        # Verify against university database
        student = StudentUniversity.query.filter_by(matric_number=matric_number).first()
        if not student:
            return jsonify({
                'success': False,
                'message': 'Matric number not found in LASU records'
            }), 404
        
        # Check if details match
        if student.full_name.lower() != full_name.lower():
            return jsonify({
                'success': False,
                'message': 'Name does not match our records'
            }), 400
        
        # Create reset request
        reset_request = PasswordResetRequest(
            matric_number=matric_number,
            full_name=full_name,
            email=email,
            phone=phone,
            faculty=faculty,
            department=department,
            status='pending'
        )
        
        db.session.add(reset_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Your request has been submitted. An administrator will review it and contact you.',
            'redirect': url_for('auth.login_page')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out user"""
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/check-matric', methods=['POST'])
def check_matric():
    """Check if matric number exists in university database (for real-time validation)"""
    try:
        data = request.get_json()
        matric = data.get('matric_number', '').strip().upper()
        
        if not matric or len(matric) < 9:
            return jsonify({
                'exists': False, 
                'is_registered': False,
                'is_graduated': False,
                'message': ''
            }), 200
        
        # First validate format
        if not is_valid_matric_number(matric):
            return jsonify({
                'exists': False,
                'is_registered': False,
                'is_graduated': False,
                'message': 'Invalid format. Must be 9 digits.'
            }), 200
        
        student = StudentUniversity.query.filter_by(matric_number=matric).first()
        
        if student:
            # Check if student is graduated/inactive
            if not student.is_active:
                return jsonify({
                    'exists': False,
                    'is_registered': False,
                    'is_graduated': True,
                    'message': student.status_note or 'You have graduated from LASU. Campus Compass is for current students only.'
                }), 200
            
            # Active student
            user = User.query.filter_by(matric_number=matric).first()
            if user:
                return jsonify({
                    'exists': True,
                    'is_registered': True,
                    'is_graduated': False,
                    'message': 'Already registered. Please login instead.'
                }), 200
            return jsonify({
                'exists': True,
                'is_registered': False,
                'is_graduated': False,
                'name': student.full_name,
                'message': f'Welcome {student.full_name}!'
            }), 200
        else:
            return jsonify({
                'exists': False,
                'is_registered': False,
                'is_graduated': False,
                'message': 'Matric number not found'
            }), 200
        
    except Exception as e:
        print(f"Error in check_matric: {str(e)}")
        return jsonify({
            'exists': False,
            'is_registered': False,
            'is_graduated': False,
            'message': 'Error verifying matric number'
        }), 200