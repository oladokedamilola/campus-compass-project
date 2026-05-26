"""
Campus Compass - Seed Student University Database
Run this script to load student data from JSON into the database
Run with: python seed_student_database.py
"""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import StudentUniversity

def seed_student_database():
    """Load student data from JSON file into database"""
    
    app = create_app()
    
    with app.app_context():
        # Load JSON data
        json_path = os.path.join('static', 'data', 'students.json')
        
        if not os.path.exists(json_path):
            print(f"❌ JSON file not found: {json_path}")
            print("Please ensure static/data/students.json exists")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        students = data.get('students', [])
        
        if not students:
            print("❌ No students found in JSON file")
            return
        
        # Count existing records
        existing_count = StudentUniversity.query.count()
        if existing_count > 0:
            print(f"⚠️ Database already has {existing_count} student records")
            response = input("Do you want to clear existing records and re-import? (y/n): ")
            if response.lower() == 'y':
                print("Clearing existing student records...")
                StudentUniversity.query.delete()
                db.session.commit()
            else:
                print("Skipping import. Existing records preserved.")
                return
        
        # Import students
        imported = 0
        for student in students:
            # Check if already exists
            existing = StudentUniversity.query.filter_by(matric_number=student['matric_number']).first()
            if existing:
                print(f"⚠️ Skipping {student['matric_number']} - already exists")
                continue
            
            new_student = StudentUniversity(
                matric_number=student['matric_number'],
                full_name=student['full_name'],
                email=student['email'],
                faculty=student['faculty'],
                department=student['department'],
                phone=student.get('phone', ''),
                year_of_admission=student['year_of_admission'],
                is_active=student.get('is_active', True),
                has_registered=student.get('has_registered', False),
                status_note=student.get('status_note', None)
            )
            db.session.add(new_student)
            imported += 1
        
        db.session.commit()
        
        print("=" * 60)
        print("✅ Student University Database Seeded Successfully!")
        print("=" * 60)
        print(f"Total students in JSON: {len(students)}")
        print(f"New students imported: {imported}")
        print(f"Total in database: {StudentUniversity.query.count()}")
        print("=" * 60)
        
        # Show sample students
        print("\n📚 Sample Students:")
        sample = StudentUniversity.query.limit(5).all()
        for s in sample:
            print(f"   {s.matric_number} - {s.full_name} - {s.department}")

if __name__ == '__main__':
    seed_student_database()