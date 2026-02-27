from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import User


def role_required(*allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    
    Usage:
        @role_required('ADMIN', 'LECTURER')
