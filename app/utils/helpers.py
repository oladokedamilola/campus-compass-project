"""
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
