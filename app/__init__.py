"""
Campus Compass - Flask Application Factory
Initializes the app, database, login manager, and registers blueprints
"""

from flask import Flask, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate  # ADD THIS IMPORT
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions (NO models imported here)
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()  # ADD THIS

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
    
    # PWA: Ensure proper MIME types
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)  # ADD THIS - Initialize Flask-Migrate
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Import models INSIDE the function to avoid circular import
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Required by Flask-Login to reload user from session"""
        return User.query.get(int(user_id))
    
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
    
    # Create database tables if they don't exist (for first run)
    with app.app_context():
        db.create_all()
    
    return app