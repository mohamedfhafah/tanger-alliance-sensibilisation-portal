from functools import wraps
from flask import abort, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated first
        if not current_user.is_authenticated:
            # Let Flask-Login handle the redirect to login
            return redirect(url_for('auth.login', next=request.url))
        
        # User is authenticated, now check admin role
        if not current_user.is_admin():
            abort(403)  # Forbidden - user is authenticated but not admin
        return f(*args, **kwargs)
    return decorated_function
