from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm

from apps.academics.models import Semester
from apps.enrollment.models import Enrollment
from apps.accounts.models import StudentProfile


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        # Add extra fields
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        
        if form.is_valid():
            user = form.save(commit=False)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.save()
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('accounts:login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
    """Student dashboard with their enrollment information"""
    
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        student_profile = None
    
    active_semester = Semester.objects.filter(is_active=True).first()
    
    # Get student's enrollments
    if student_profile:
        enrollments = Enrollment.objects.filter(
            student=student_profile
        ).select_related('course', 'semester')
        
        # Current semester enrollments
        if active_semester:
            current_enrollments = enrollments.filter(semester=active_semester)
            registered_courses = current_enrollments.count()
            total_credits = current_enrollments.filter(
                status='APPROVED'
            ).aggregate(
                total=Sum('course__credit_units')
            )['total'] or 0
        else:
            current_enrollments = []
            registered_courses = 0
            total_credits = 0
    else:
        current_enrollments = []
        registered_courses = 0
        total_credits = 0
    
    # Calculate available seats (total capacity - enrolled)
    available_seats = 0
    if active_semester:
        from apps.academics.models import Course
        total_capacity = Course.objects.filter(is_active=True).aggregate(
            total=Sum('capacity')
        )['total'] or 0
        enrolled = Enrollment.objects.filter(
            semester=active_semester,
            status='APPROVED'
        ).count()
        available_seats = max(0, total_capacity - enrolled)
    
    context = {
        'student_profile': student_profile,
        'active_semester': str(active_semester) if active_semester else None,
        'registered_courses': registered_courses,
        'total_credits': total_credits,
        'available_seats': available_seats,
        'my_courses': current_enrollments if active_semester else [],
    }
    
    return render(request, 'dashboard/student_dashboard.html', context)
