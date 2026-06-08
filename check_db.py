"""
Check database contents
Run with: python check_db.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, StudentUniversity

def check_db():
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("DATABASE CONTENTS")
        print("=" * 50)
        
        # Check Users
        users = User.query.all()
        print(f"\n📋 Users ({len(users)}):")
        for user in users:
            print(f"   - {user.matric_number} | {user.full_name} | {user.user_type}")
        
        # Check Students
        students = StudentUniversity.query.all()
        print(f"\n📚 Students ({len(students)}):")
        for student in students:
            print(f"   - {student.matric_number} | {student.full_name} | {student.department}")
        
        print("\n" + "=" * 50)

if __name__ == '__main__':
    check_db()