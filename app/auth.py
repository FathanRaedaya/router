from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from .models import PaymentMethod

# Wrapper for pages where subscription is required
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if not PaymentMethod.query.filter_by(user_id=current_user.id).first():
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Wrapper for pages where admin is required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if not current_user.admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Wrapper for pages where admin is not allowed
def admin_not_allowed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if current_user.admin:
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return decorated_function
