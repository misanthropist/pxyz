from functools import wraps
from flask import redirect, session, url_for, abort
from pxyz.models import User

def login_require(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user_name = session.get('login_user')
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return redirect(url_for('user.login'))
        return func(*args, **kwargs)
    return decorated_function

def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            user_name = session.get('login_user')
            user = User.query.filter_by(username=user_name).first()
            if user and not user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator

