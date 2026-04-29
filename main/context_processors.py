def user_session(request):
    """Add user session info to all templates"""
    email = request.session.get('user_email')
    return {
        'user_session': {
            'email': email,
            'role': request.session.get('user_role'),
            'is_authenticated': bool(email),
        }
    }