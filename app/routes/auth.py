"""
Campus Compass - Authentication Routes
Matric Number-based Authentication System
Students verify with matric number first, then create password
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import generate_csrf
from app import db, csrf
from app.models import User, StudentUniversity, PasswordResetRequest
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """Return a fresh CSRF token for AJAX requests"""
    from flask_wtf.csrf import generate_csrf
    csrf_token = generate_csrf()
    return jsonify({'csrf_token': csrf_token})

def is_valid_matric_number(matric):
    """
    Validate student matric number format.
    Accepts exactly 9 digits.
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
    return True


def is_valid_staff_id(staff_id):
    """
    Validate staff/admin ID format.
    Accepts alphanumeric (letters and numbers) with length between 4-20 characters.
    """
    if not staff_id:
        return False
    
    pattern = r'^[A-Za-z0-9]{4,20}$'
    return bool(re.match(pattern, staff_id))


@auth_bp.route('/verify-matric', methods=['GET'])
def verify_matric_page():
    """Page to verify matric number before registration"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard.index'))
    
    from flask import make_response
    response = make_response(render_template('verify_matric.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# IMPORTANT: This is the POST endpoint for verification - MUST be exempt from CSRF
@auth_bp.route('/verify-matric', methods=['POST'])
@csrf.exempt
def verify_matric():
    """Verify matric number against university database"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid request. Please refresh and try again.'
            }), 400
        
        matric_number = data.get('matric_number', '').strip().upper()
        
        # Validation
        if not matric_number:
            return jsonify({
                'success': False,
                'message': 'Please enter your matric number'
            }), 400
        
        if len(matric_number) != 9 or not matric_number.isdigit():
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
        session.permanent = True
        session['verified_matric'] = matric_number
        session['student_data'] = {
            'full_name': student_record.full_name,
            'email': student_record.email,
            'faculty': student_record.faculty,
            'department': student_record.department,
            'phone': student_record.phone
        }
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'Welcome {student_record.full_name}! Please complete your registration.',
            'redirect': url_for('auth.register_page')
        })
        
    except Exception as e:
        print(f"Error in verify_matric: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Render login page"""
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard.index'))
    
    # Create response object from rendered template
    from flask import make_response
    response = make_response(render_template('login.html'))
    
    # Prevent caching of the login page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@auth_bp.route('/login', methods=['POST'])
def login():
    """Process login with matric number and password (students only)"""
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
        print(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/staff-login', methods=['GET'])
def staff_login_page():
    """Render staff/admin login page"""
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('dashboard.index'))
    return render_template('staff_login.html')


# IMPORTANT: Staff login needs CSRF protection for production, but exempt for testing
@auth_bp.route('/staff-login', methods=['POST'])
@csrf.exempt  # Temporarily exempt for testing
def staff_login():
    """Process staff/admin login with staff ID (alphanumeric) and password"""
    try:
        data = request.get_json()
        
        # Debug logging
        print(f"[DEBUG] Staff login request received")
        print(f"[DEBUG] Request data: {data}")
        
        # Get staff_id (handle both field names)
        staff_id = data.get('staff_id', '')
        if not staff_id:
            staff_id = data.get('matric_number', '')
        
        staff_id = staff_id.strip().upper()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        print(f"[DEBUG] Staff ID: {staff_id}")
        print(f"[DEBUG] Password length: {len(password)}")
        
        # Validation
        if not staff_id or not password:
            return jsonify({
                'success': False,
                'message': 'Please enter both staff ID and password'
            }), 400
        
        if not is_valid_staff_id(staff_id):
            return jsonify({
                'success': False,
                'message': 'Invalid staff ID format. Use 4-20 alphanumeric characters (e.g., ADMIN0001).'
            }), 400
        
        # Find user by matric_number (which stores staff ID for admin users)
        user = User.query.filter_by(matric_number=staff_id).first()
        
        print(f"[DEBUG] User found: {user is not None}")
        if user:
            print(f"[DEBUG] User type: {user.user_type}")
            print(f"[DEBUG] Is admin: {user.is_admin()}")
        
        # Check credentials
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid staff ID or password'
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
        print(f"[ERROR] Staff login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Render registration page (after matric verification)"""
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard.index'))
    
    # Check if matric was verified
    if 'verified_matric' not in session:
        flash('Please verify your matric number first.', 'warning')
        return redirect(url_for('auth.verify_matric_page'))
    
    # Create response object from rendered template
    from flask import make_response
    response = make_response(render_template('register.html'))
    
    # Prevent caching of the register page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


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
        import traceback
        traceback.print_exc()
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
        print(f"Forgot password error: {str(e)}")
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
    # Redirect with a cache-busting timestamp parameter
    from flask import make_response
    response = redirect(url_for('auth.login_page', _external=True) + '?t=' + str(int(datetime.now().timestamp())))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check current session status - for client-side validation"""
    from flask import jsonify
    
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user_type': current_user.user_type,
            'user_name': current_user.full_name.split()[0] if current_user.full_name else '',
            'is_admin': current_user.is_admin(),
            'redirect_url': url_for('admin.index') if current_user.is_admin() else url_for('dashboard.index')
        })
    else:
        return jsonify({
            'authenticated': False,
            'redirect_url': url_for('auth.login_page')
        })

# Public endpoint - Exempt from CSRF
@auth_bp.route('/check-matric', methods=['POST'])
@csrf.exempt
def check_matric():
    """Check if matric number exists in university database (for real-time validation)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'exists': False,
                'is_registered': False,
                'is_graduated': False,
                'message': 'Invalid request. Please refresh and try again.'
            }), 200
        
        matric = data.get('matric_number', '').strip().upper()
        
        if not matric:
            return jsonify({
                'exists': False,
                'is_registered': False,
                'is_graduated': False,
                'message': ''
            }), 200
        
        # Check length
        if len(matric) != 9 or not matric.isdigit():
            return jsonify({
                'exists': False,
                'is_registered': False,
                'is_graduated': False,
                'message': 'Matric number must be exactly 9 digits.'
            }), 200
        
        # Check in database
        student = StudentUniversity.query.filter_by(matric_number=matric).first()
        
        if student:
            if not student.is_active:
                return jsonify({
                    'exists': False,
                    'is_registered': False,
                    'is_graduated': True,
                    'message': student.status_note or 'You have graduated from LASU. Campus Compass is for current students only.'
                }), 200
            
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
                'message': 'Matric number not found in LASU records.'
            }), 200
        
    except Exception as e:
        print(f"Error in check_matric: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'exists': False,
            'is_registered': False,
            'is_graduated': False,
            'message': 'Error verifying matric number. Please try again.'
        }), 200