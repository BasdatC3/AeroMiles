"""Helper auth & session yang dipakai semua app."""
import hashlib
from functools import wraps
from django.shortcuts import redirect


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_session_user(request):
    return (
        request.session.get('user_email'),
        request.session.get('user_role'),
    )


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_email'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            email = request.session.get('user_email')
            role = request.session.get('user_role')
            if not email:
                return redirect('login')
            if role not in roles:
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
