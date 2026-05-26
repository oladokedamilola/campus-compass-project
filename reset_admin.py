"""
Campus Compass - Admin Password Reset
Run with: python reset_admin.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def reset_admin_password():
    """Reset admin user password"""
    
    app = create_app()
    
    with app.app_context():
        admin = User.query.filter_by(email='admin@campus.com').first()
        
        if not admin:
            print("❌ Admin user not found. Run python seed_admin.py first.")
            return
        
        new_password = input("Enter new admin password (min 6 chars): ").strip()
        
        if len(new_password) < 6:
            print("❌ Password must be at least 6 characters.")
            return
        
        admin.set_password(new_password)
        db.session.commit()
        
        print("✅ Admin password reset successfully!")

if __name__ == '__main__':
    reset_admin_password()