"""
Campus Compass - Database Models
User model with role-based access (Student/Admin)
StudentUniversity model for LASU student database
SavedLocations model for favorites feature
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Use a relative import instead of absolute
from . import db

class User(UserMixin, db.Model):
    """User model for authentication and role management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    matric_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='student')
    faculty = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    
    # Relationship for saved favorites
    saved_locations = db.relationship('SavedLocation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.user_type == 'admin'
    
    def is_student(self):
        """Check if user has student role"""
        return self.user_type == 'student'
    
    def update_last_login(self):
        """Update the last_login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses"""
        return {
            'id': self.id,
            'matric_number': self.matric_number,
            'full_name': self.full_name,
            'user_type': self.user_type,
            'faculty': self.faculty,
            'department': self.department,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.matric_number}>'


class StudentUniversity(db.Model):
    """University student database (LASU records)"""
    __tablename__ = 'student_university'
    
    id = db.Column(db.Integer, primary_key=True)
    matric_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    year_of_admission = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    has_registered = db.Column(db.Boolean, default=False)
    status_note = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'matric_number': self.matric_number,
            'full_name': self.full_name,
            'email': self.email,
            'faculty': self.faculty,
            'department': self.department,
            'phone': self.phone,
            'year_of_admission': self.year_of_admission,
            'is_active': self.is_active,
            'has_registered': self.has_registered
        }
    
    def __repr__(self):
        return f'<StudentUniversity {self.matric_number}>'


class PasswordResetRequest(db.Model):
    """Password reset requests from students"""
    __tablename__ = 'password_reset_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    matric_number = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'matric_number': self.matric_number,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'faculty': self.faculty,
            'department': self.department,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PasswordResetRequest {self.matric_number} - {self.status}>'


class SavedLocation(db.Model):
    """Saved locations model for user favorites"""
    __tablename__ = 'saved_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_name = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    building_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert saved location to dictionary for JSON responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'place_name': self.place_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'building_type': self.building_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SavedLocation {self.place_name} - User {self.user_id}>'