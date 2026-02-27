from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import User


def role_required(*allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    
    Usage:
        @role_required('ADMIN', 'LECTURER')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden(
                    f"Access denied. This view requires {', '.join(allowed_roles)} role(s)."
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def student_required(view_func):
    """Decorator to restrict access to students only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_student:
            return HttpResponseForbidden("Access denied. This view is for students only.")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def lecturer_required(view_func):
    """Decorator to restrict access to lecturers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_lecturer:
            return HttpResponseForbidden("Access denied. This view is for lecturers only.")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to restrict access to admins only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_admin_user:
            return HttpResponseForbidden("Access denied. This view is for administrators only.")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_lecturer_required(view_func):
    """Decorator to restrict access to admins and lecturers"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        allowed = [User.Role.ADMIN, User.Role.LECTURER]
        if request.user.role not in allowed:
            return HttpResponseForbidden(
                "Access denied. This view requires Admin or Lecturer role."
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper
