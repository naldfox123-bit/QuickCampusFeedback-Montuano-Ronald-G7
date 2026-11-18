from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role):
    """Only let users with the given role open the view; others go to their own dashboard."""
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                messages.error(request, 'You do not have access to that page.')
                return redirect('dashboard:home')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
