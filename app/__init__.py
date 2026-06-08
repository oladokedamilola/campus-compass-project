"""
Campus Compass - Flask Application Factory
Initializes the app, database, login manager, and registers blueprints
"""

from flask import Flask, send_from_directory, render_template, redirect, url_for, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///campus.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_PERMANENT'] = True
    
    # Disable static file caching
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # Force template reload
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # ============================================
    # GLOBAL BEFORE REQUEST - WITH PUBLIC PAGE REDIRECTS
    # ============================================
    
    @app.before_request
    def auth_redirects():
        """Handle authentication redirects - Redirects authenticated users from public pages"""
        
        # Normalize the path (remove trailing slash for comparison)
        path = request.path.rstrip('/')
        
        # Auth pages that logged-in users should NOT access
        auth_pages = [
            '/auth/login',
            '/auth/register',
            '/auth/verify-matric',
            '/auth/forgot-password',
            '/auth/staff-login'
        ]
        
        # Public pages that should redirect authenticated users to dashboard
        # (landing pages that don't make sense for logged-in users)
        public_pages_redirect_auth = [
            '/',
            '/index',
            '/test-matric'
        ]
        
        # Protected pages that require login
        protected_prefixes = [
            '/dashboard',
            '/favorites',
            '/profile',
            '/admin'
        ]
        
        # Check if current path is an auth page (using normalized path)
        is_auth_page = any(path == page or path.startswith(page + '?') for page in auth_pages)
        
        # Check if current path is a public page that should redirect authenticated users
        is_public_redirect = any(path == page or path.startswith(page + '?') for page in public_pages_redirect_auth)
        
        # Check if current path is protected
        is_protected = any(path.startswith(prefix) for prefix in protected_prefixes)
        
        # Also check the map authenticated route
        if path == '/map' or path.startswith('/map/index'):
            is_protected = True
        
        # Also check locations authenticated route
        if path == '/locations' or path.startswith('/locations'):
            # Only redirect if it's not the public locations page
            if not path.startswith('/locations/public'):
                is_protected = True
        
        # Redirect authenticated users away from auth pages
        if current_user.is_authenticated and is_auth_page:
            from flask import flash
            flash('You are already logged in.', 'info')
            if current_user.is_admin():
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('dashboard.index'))
        
        # NEW: Redirect authenticated users away from public landing pages (home page, etc.)
        if current_user.is_authenticated and is_public_redirect:
            # Don't flash a message for these redirects (silent redirect)
            if current_user.is_admin():
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('dashboard.index'))
        
        # Redirect unauthenticated users away from protected pages
        if not current_user.is_authenticated and is_protected:
            from flask import flash
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login_page'))
    
    @app.after_request
    def force_no_cache(response):
        """Force no-cache headers - FIXED: single Cache-Control header"""
        # Single, clear cache header (not duplicate)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Prevent bfcache
        response.headers['Cache-Control'] += ', no-transform'
        
        return response
    
    # Configure login
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Import models
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ============================================
    # SERVE CAMPUS IMAGES
    # ============================================
    @app.route('/static/campus-images/<path:filename>')
    def serve_campus_images(filename):
        campus_images_path = os.path.join(app.root_path, 'static', 'campus-images')
        response = send_from_directory(campus_images_path, filename)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.map import map_bp
    from app.routes.admin import admin_bp
    from app.routes.upload import upload_bp
        
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(map_bp, url_prefix='/map')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    # PWA routes
    @app.route('/sw.js')
    def service_worker():
        response = send_from_directory('.', 'sw.js', mimetype='application/javascript')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Service-Worker-Allowed'] = '/'
        return response
    
    @app.route('/manifest.json')
    def manifest():
        response = send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    @app.route('/offline')
    def offline():
        return render_template('offline.html')

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(401)
    def unauthorized(e):
        return redirect(url_for('auth.login_page'))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app