from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.contrib.auth.decorators import login_required

from apps.accounts.models import User, StudentProfile
from apps.academics.models import Programme, Course, Semester
from apps.enrollment.models import Enrollment


@login_required
def dashboard(request):
    """Admin dashboard with system overview and reports"""
    
    # Get active semester
    active_semester = Semester.objects.filter(is_active=True).first()
    
    # Basic stats
    total_students = StudentProfile.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_programmes = Programme.objects.filter(is_active=True).count()
    
    # Enrollment stats
    if active_semester:
        pending_enrollments = Enrollment.objects.filter(
            semester=active_semester,
            status='PENDING'
        ).count()
        
        approved_enrollments = Enrollment.objects.filter(
            semester=active_semester,
            status='APPROVED'
        ).count()
    else:
        pending_enrollments = 0
        approved_enrollments = 0
    
    # Top courses by enrollment
    top_courses = Course.objects.filter(
        is_active=True
    ).annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__status='APPROVED'))
    ).order_by('-enrollment_count')[:5]
    
    # Courses at capacity
    courses_at_capacity = []
    for course in Course.objects.filter(is_active=True):
        if course.is_full:
            courses_at_capacity.append(course)
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_programmes': total_programmes,
        'active_semester': str(active_semester) if active_semester else None,
        'pending_enrollments': pending_enrollments,
        'approved_enrollments': approved_enrollments,
        'top_courses': top_courses,
        'courses_at_capacity': courses_at_capacity,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def enrollment_report(request):
    """Generate enrollment report by programme"""
    
    # Get filter parameters
    programme_id = request.GET.get('programme')
    semester_id = request.GET.get('semester')
    
    # Base query
    enrollments = Enrollment.objects.select_related(
        'student__user', 'course__programme', 'semester'
    )
    
    if programme_id:
        enrollments = enrollments.filter(course__programme_id=programme_id)
    
    if semester_id:
        enrollments = enrollments.filter(semester_id=semester_id)
    
    # Group by programme
    programme_stats = []
    for programme in Programme.objects.filter(is_active=True):
        prog_enrollments = enrollments.filter(course__programme=programme)
        programme_stats.append({
            'programme': programme,
            'total': prog_enrollments.count(),
            'approved': prog_enrollments.filter(status='APPROVED').count(),
            'pending': prog_enrollments.filter(status='PENDING').count(),
            'dropped': prog_enrollments.filter(status='DROPPED').count(),
        })
    
    context = {
        'programme_stats': programme_stats,
        'programmes': Programme.objects.filter(is_active=True),
        'semesters': Semester.objects.all(),
    }
    
    return render(request, 'reporting/enrollment_report.html', context)


@login_required
def course_popularity(request):
    """Course popularity report"""
    
    courses = Course.objects.filter(
        is_active=True
    ).annotate(
        total_enrolled=Count('enrollments', filter=Q(enrollments__status='APPROVED')),
        pending=Count('enrollments', filter=Q(enrollments__status='PENDING')),
    ).order_by('-total_enrolled')
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'reporting/course_popularity.html', context)


@login_required
def lecturer_load(request):
    """Lecturer workload report"""
    
    from apps.accounts.models import User
    
    lecturers = User.objects.filter(
        role='LECTURER'
    ).annotate(
        courses_taught=Count('taught_courses'),
        total_students=Count('taught_courses__enrollments', 
                           filter=Q(taught_courses__enrollments__status='APPROVED'))
    )
    
    context = {
        'lecturers': lecturers,
    }
    
    return render(request, 'reporting/lecturer_load.html', context)
