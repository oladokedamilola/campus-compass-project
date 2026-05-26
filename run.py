"""
Campus Compass - Application Entry Point
Run with: python run.py (development) or gunicorn run:app (production)
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
