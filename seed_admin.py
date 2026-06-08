"""
Campus Compass - Admin User Seeder
Run this script to create the default admin user
Run with: python seed_admin.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def seed_admin():
    """Create default admin user if it doesn't exist"""
    
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists (using matric number as identifier)
        admin_matric = 'ADMIN0001'
        existing_admin = User.query.filter_by(matric_number=admin_matric).first()
        
        if existing_admin:
            print(f"Admin user already exists: {admin_matric}")
            print(f"Password reset? Run: python reset_admin.py")
            return
        
        # Create admin user
        admin = User(
            matric_number=admin_matric,
            full_name='System Administrator',
            user_type='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 50)
        print("✅ Default admin user created successfully!")
        print("=" * 50)
        print(f"Matric Number: {admin_matric}")
        print(f"Password:      admin123")
        print("=" * 50)
        print("\n⚠️  Please change this password after first login!")

if __name__ == '__main__':
    seed_admin()