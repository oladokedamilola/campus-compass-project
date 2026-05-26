#!/usr/bin/env python3
"""
Campus Compass - Project Setup Script
Run this script to create the complete file structure and all files.
Usage: python setup_campus_compass.py
"""

import os
import stat

# Project root directory (current directory)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define all folders to create
FOLDERS = [
    "app",
    "app/routes",
    "app/templates",
    "app/templates/admin",
    "app/static/css",
    "app/static/js",
    "app/static/images",
    "app/utils",
    "instance",
    "migrations",
]

# Define all files and their content
FILES = {}

# ==================== ROOT FILES ====================

# run.py
FILES["run.py"] = '''"""
Campus Compass - Application Entry Point
Run with: python run.py (development) or gunicorn run:app (production)
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

# requirements.txt (no version pinning)
FILES["requirements.txt"] = '''Flask
Flask-SQLAlchemy
Flask-Login
Flask-WTF
WTForms
python-dotenv
email-validator
werkzeug
bcrypt
gunicorn
'''

# .env (template)
FILES[".env"] = '''FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///campus.db
'''

# .gitignore
FILES[".gitignore"] = '''# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.env
.venv
.venv/

# Database
instance/
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Render deployment
render.yaml.local

# Environment
.env.local
.env.production
'''

# sw.js (Service Worker - root directory)
FILES["sw.js"] = '''// Campus Compass - Service Worker
// Enables offline functionality and PWA installation

const CACHE_NAME = 'campus-compass-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/manifest.json'
];

// Install event - cache core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache first, fall back to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
'''

# render.yaml (optional)
FILES["render.yaml"] = '''services:
  - type: web
    name: campus-compass
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: campus-compass-db
          property: connectionString

databases:
  - name: campus-compass-db
    plan: free
'''

# ==================== APP/__INIT__.PY ====================

FILES["app/__init__.py"] = '''"""
Campus Compass - Flask Application Factory
Initializes the app, database, login manager, and registers blueprints
"""

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///campus.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # PWA: Ensure proper MIME types for service worker and manifest
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Import models (must be after db initialization)
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
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(map_bp, url_prefix='/map')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # PWA: Serve service worker from root
    @app.route('/sw.js')
    def service_worker():
        """Serve service worker from root directory for proper scope"""
        return send_from_directory('.', 'sw.js', mimetype='application/javascript')
    
    # PWA: Serve manifest from static folder (but accessible at /manifest.json)
    @app.route('/manifest.json')
    def manifest():
        """Serve manifest file for PWA installation"""
        return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
'''

# ==================== APP/MODELS.PY ====================

FILES["app/models.py"] = '''"""
Campus Compass - Database Models
User model with role-based access (Student/Admin)
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    """User model for authentication and role management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    matric_number = db.Column(db.String(20), nullable=True)  # Only for students
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship for saved favorites (future feature)
    # saved_locations = db.relationship('SavedLocation', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password, method='bcrypt')
    
    def check_password(self, password):
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.user_type == 'admin'
    
    def __repr__(self):
        return f'<User {self.email}>'

# Future: SavedLocation model for favorites
# class SavedLocation(db.Model):
#     __tablename__ = 'saved_locations'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     place_name = db.Column(db.String(150), nullable=False)
#     latitude = db.Column(db.Float, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)
#     description = db.Column(db.String(300), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
'''

# ==================== APP/ROUTES/__INIT__.PY ====================

FILES["app/routes/__init__.py"] = '''"""
Routes Blueprints Initialization
"""
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.dashboard import dashboard_bp
from app.routes.map import map_bp
from app.routes.admin import admin_bp
'''

# ==================== APP/ROUTES/MAIN.PY ====================

FILES["app/routes/main.py"] = '''"""
Campus Compass - Public Routes (Home, etc.)
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page (optional)"""
    return render_template('about.html')
'''

# ==================== APP/ROUTES/AUTH.PY ====================

FILES["app/routes/auth.py"] = '''"""
Campus Compass - Authentication Routes (Placeholder)
Full implementation in Phase 4
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Render login page"""
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Process login (AJAX) - to be implemented in Phase 4"""
    return jsonify({'success': False, 'message': 'Implementation pending'})

@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Render registration page"""
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Process registration (AJAX) - to be implemented in Phase 4"""
    return jsonify({'success': False, 'message': 'Implementation pending'})

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out user"""
    logout_user()
    return redirect(url_for('main.index'))
'''

# ==================== APP/ROUTES/DASHBOARD.PY ====================

FILES["app/routes/dashboard.py"] = '''"""
Campus Compass - Dashboard Routes (Placeholder)
Full implementation in Phase 5
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """User dashboard"""
    return render_template('dashboard.html', user=current_user)
'''

# ==================== APP/ROUTES/MAP.PY ====================

FILES["app/routes/map.py"] = '''"""
Campus Compass - Map Routes (Placeholder)
Full implementation in Phase 6
"""

from flask import Blueprint, render_template
from flask_login import login_required

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
@login_required
def index():
    """Full-screen map page"""
    return render_template('map.html')
'''

# ==================== APP/ROUTES/ADMIN.PY ====================

FILES["app/routes/admin.py"] = '''"""
Campus Compass - Admin Routes (Placeholder)
Full implementation in Phase 8
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to restrict access to admin users"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')
'''

# ==================== APP/UTILS/__INIT__.PY ====================

FILES["app/utils/__init__.py"] = '''"""
Utils Package
"""
from app.utils.helpers import *
'''

# ==================== APP/UTILS/HELPERS.PY ====================

FILES["app/utils/helpers.py"] = '''"""
Campus Compass - Helper Utilities
"""

import re
from flask import flash

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def flash_errors(form):
    """Flash all form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
'''

# ==================== TEMPLATES ====================

FILES["app/templates/index.html"] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Campus Compass - LASU Navigation</title>
</head>
<body>
    <h1>Campus Compass</h1>
    <p>Navigation app for LASU Ojo Campus</p>
    <p>Phase 1 - Setup Complete!</p>
</body>
</html>
'''

FILES["app/templates/base_public.html"] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Campus Compass - {% block title %}{% endblock %}</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <!-- Public Base Template - Will be implemented in Phase 3 -->
    {% block content %}{% endblock %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

FILES["app/templates/base_user.html"] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Campus Compass - {% block title %}{% endblock %}</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <!-- User Base Template - Will be implemented in Phase 3 -->
    {% block content %}{% endblock %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

FILES["app/templates/login.html"] = "{% extends 'base_public.html' %}{% block content %}<h1>Login - Coming Soon</h1>{% endblock %}"
FILES["app/templates/register.html"] = "{% extends 'base_public.html' %}{% block content %}<h1>Register - Coming Soon</h1>{% endblock %}"
FILES["app/templates/dashboard.html"] = "{% extends 'base_user.html' %}{% block content %}<h1>Dashboard - Coming Soon</h1>{% endblock %}"
FILES["app/templates/map.html"] = "{% extends 'base_user.html' %}{% block content %}<h1>Map - Coming Soon</h1>{% endblock %}"
FILES["app/templates/admin/dashboard.html"] = "{% extends 'base_user.html' %}{% block content %}<h1>Admin Dashboard - Coming Soon</h1>{% endblock %}"

# ==================== STATIC FILES ====================

# manifest.json
FILES["static/manifest.json"] = '''{
  "name": "Campus Compass",
  "short_name": "CampusComp",
  "description": "Navigation app for LASU Ojo Campus",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "theme_color": "#0D0D0D",
  "background_color": "#0D0D0D",
  "icons": [
    {
      "src": "/static/images/icon-72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/static/images/icon-96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-144.png",
      "sizes": "144x144",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-152.png",
      "sizes": "152x152",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
'''

# static/js/main.js
FILES["static/js/main.js"] = '''// Campus Compass - Main JavaScript
// PWA registration and common utilities

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('Service Worker registered with scope:', registration.scope);
      })
      .catch(error => {
        console.log('Service Worker registration failed:', error);
      });
  });
}

// Check if app is running in standalone mode (PWA installed)
if (window.matchMedia('(display-mode: standalone)').matches) {
  console.log('App is running as installed PWA');
}
'''

# static/css/style.css (Neo Compass Concept - Condensed)
FILES["static/css/style.css"] = '''/* ============================================
   CAMPUS COMPASS - NEO COMPASS CONCEPT
   Brand Identity Styles (Bootstrap 5 Compatible)
   ============================================ */

:root {
  --campus-primary-dark: #0D0D0D;
  --campus-primary-white: #FFFFFF;
  --campus-accent: #00F0FF;
  --campus-accent-dark: #00C8D4;
  --campus-accent-soft: rgba(0, 240, 255, 0.15);
  --campus-gray-800: #212121;
  --campus-gray-700: #424242;
  --campus-gray-600: #616161;
  --campus-gray-500: #9E9E9E;
  --campus-glass-bg: rgba(255, 255, 255, 0.08);
  --campus-glass-border: rgba(255, 255, 255, 0.12);
  --campus-font-heading: 'Clash Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --campus-font-body: 'Satoshi', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --campus-radius-lg: 20px;
  --campus-shadow-glow: 0 0 20px rgba(0, 240, 255, 0.3);
}

body {
  background-color: var(--campus-primary-dark);
  color: var(--campus-primary-white);
  font-family: var(--campus-font-body);
}

.btn-campus-accent {
  background-color: var(--campus-accent);
  color: var(--campus-primary-dark);
  border: none;
  border-radius: 12px;
  padding: 10px 24px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-campus-accent:hover {
  background-color: var(--campus-accent-dark);
  box-shadow: var(--campus-shadow-glow);
  transform: translateY(-1px);
}

.campus-glass-card {
  background: var(--campus-glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--campus-glass-border);
  border-radius: var(--campus-radius-lg);
  padding: 20px;
}
'''

# ==================== CREATE A README FILE ====================

FILES["README.txt"] = '''Campus Compass - LASU Campus Navigation PWA

Setup Instructions:
1. Run this setup script to create all files
2. Create virtual environment: python -m venv venv
3. Activate it: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)
4. Install dependencies: pip install -r requirements.txt
5. Run the app: python run.py
6. Visit: http://localhost:5000

Admin account creation (run in Python shell):
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
...     admin = User(email='admin@campus.com', full_name='Admin User', user_type='admin')
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
'''

# ==================== HELPER FUNCTION ====================

def create_project():
    """Create all folders and files"""
    
    print("=" * 60)
    print("🚀 Campus Compass - Project Setup Script")
    print("=" * 60)
    
    # Create folders
    print("\n📁 Creating folders...")
    for folder in FOLDERS:
        folder_path = os.path.join(PROJECT_ROOT, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"   ✓ Created: {folder}")
    
    # Create files
    print("\n📝 Creating files...")
    for file_path, content in FILES.items():
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(full_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✓ Created: {file_path}")
    
    # Make run.py executable (Unix-like systems)
    run_path = os.path.join(PROJECT_ROOT, "run.py")
    if os.name != 'nt':  # Not Windows
        st = os.stat(run_path)
        os.chmod(run_path, st.st_mode | stat.S_IEXEC)
    
    print("\n" + "=" * 60)
    print("✅ Project setup complete!")
    print("=" * 60)
    
    print("\n📋 Next steps:")
    print("1. Create virtual environment:")
    print("   python -m venv venv")
    print("\n2. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Mac/Linux: source venv/bin/activate")
    print("\n3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n4. Run the application:")
    print("   python run.py")
    print("\n5. Open your browser and visit:")
    print("   http://localhost:5000")
    print("\n" + "=" * 60)

# ==================== RUN THE SCRIPT ====================

if __name__ == "__main__":
    create_project()