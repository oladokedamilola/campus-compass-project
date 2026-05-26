# save as check_db.py
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if profile_image column exists
    try:
        # Try to query a user
        user = User.query.first()
        if user:
            print(f"User found: {user.full_name}")
            print(f"Has profile_image attribute: {hasattr(user, 'profile_image')}")
            if hasattr(user, 'profile_image'):
                print(f"Current profile_image value: {user.profile_image}")
        else:
            print("No users found")
            
        # Check table columns
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('users')
        print("\nColumns in users table:")
        for col in columns:
            print(f"  - {col['name']}")
    except Exception as e:
        print(f"Error: {e}")