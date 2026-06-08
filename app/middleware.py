"""
Custom middleware to enforce no-caching across all routes
This prevents browsers from caching authenticated pages and CSRF tokens
"""

from flask import request, session, current_app
from datetime import datetime
import re

class NoCacheMiddleware:
    """Middleware to add no-cache headers to all responses"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Process the request through Flask
        response = self.app(environ, start_response)
        
        # Add cache-control headers to EVERY response
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Additional headers to prevent bfcache (back/forward cache)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response.headers['Surrogate-Control'] = 'no-store'
        
        # Prevent Chrome from caching
        response.headers['Clear-Site-Data'] = '"cache"'
        
        return response


class AuthAwareRedirectMiddleware:
    """Middleware to prevent authenticated users from accessing auth pages"""
    
    # Routes that should be blocked for authenticated users
    AUTH_ROUTES = [
        '/auth/login',
        '/auth/register', 
        '/auth/verify-matric',
        '/auth/forgot-password',
        '/auth/staff-login'
    ]
    
    # Routes for authenticated users
    PROTECTED_ROUTES = [
        '/dashboard',
        '/map/',
        '/favorites',
        '/profile'
    ]
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # This is tricky with WSGI, so we'll implement in Flask's before_request instead
        # See the before_request in __init__.py
        return self.app(environ, start_response)