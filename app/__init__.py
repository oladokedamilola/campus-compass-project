"""
Campus Compass - Flask Application Factory
Initializes the app, database, login manager, and registers blueprints
"""

from flask import Flask, send_from_directory, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize extensions (NO models imported here)
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
    
    # Session configuration - FIXED for better persistence
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_PERMANENT'] = True
    
    # PWA: Ensure proper MIME types
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CSRF - EXEMPT public API endpoints properly
    @app.after_request
    def after_request(response):
        """Ensure session is saved"""
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    
    # Configure login
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Import models INSIDE the function to avoid circular import
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Required by Flask-Login to reload user from session"""
        return User.query.get(int(user_id))
    
    # ============================================
    # SERVE CAMPUS IMAGES FROM CUSTOM FOLDER
    # ============================================
    @app.route('/static/campus-images/<path:filename>')
    def serve_campus_images(filename):
        """Serve images from the campus-images folder"""
        campus_images_path = os.path.join(app.root_path, 'static', 'campus-images')
        return send_from_directory(campus_images_path, filename)
    
    # Register blueprints (routes)
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
    
    # PWA: Serve service worker from root
    @app.route('/sw.js')
    def service_worker():
        """Serve service worker from root directory for proper scope"""
        return send_from_directory('.', 'sw.js', mimetype='application/javascript')
    
    # PWA: Serve manifest from static folder
    @app.route('/manifest.json')
    def manifest():
        """Serve manifest file for PWA installation"""
        return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')
    
    # Offline fallback page
    @app.route('/offline')
    def offline():
        """Offline fallback page for PWA"""
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
    
    # Create database tables if they don't exist (for first run)
    with app.app_context():
        db.create_all()
    
    return app