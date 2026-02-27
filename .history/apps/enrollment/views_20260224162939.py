from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import Enrollment
from .forms import EnrollmentForm, EnrollmentApprovalForm, CourseRegistrationForm
from apps.academics.models import Semester, Course
from apps.accounts.models import StudentProfile
from apps.accounts.decorators import admin_required, student_required, lecturer_required, admin_or_lecturer_required


@login_required
def enrollment_list(request):
    """List all enrollments with filters"""
    enrollments = Enrollment.objects.select_related(
        'student__user', 'course__programme', 'semester'
    )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)
    
    # Filter by semester
    semester_id = request.GET.get('semester')
    if semester_id:
        enrollments = enrollments.filter(semester_id=semester_id)
    
    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'enrollments': page_obj,
        'semesters': Semester.objects.all(),
        'status_filter': status_filter,
    }
    return render(request, 'enrollment/enrollment_list.html', context)


@admin_or_lecturer_required
def enrollment_approve(request, pk):
    """Approve or reject an enrollment"""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    if request.method == 'POST':
        form = EnrollmentApprovalForm(request.POST, instance=enrollment)
        if form.is_valid():
            enrollment = form.save(commit=False)
            if enrollment.status == 'APPROVED':
                enrollment.date_approved = timezone.now()
                enrollment.approved_by = request.user
            enrollment.save()
            messages.success(request, f'Enrollment {enrollment.status.lower()}!')
            return redirect('enrollment:enrollment_list')
    else:
        form = EnrollmentApprovalForm(instance=enrollment)
    
    return render(request, 'enrollment/enrollment_form.html', {
        'form': form,
        'enrollment': enrollment
    })


@student_required
@transaction.atomic
def register_course(request, course_id):
    """Register for a course"""
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    
    # Get the active semester
    semester = Semester.objects.filter(is_active=True).first()
    if not semester:
        messages.error(request, 'No active semester for registration.')
        return redirect('academics:course_list')
    
    # Get student's profile
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'You do not have a student profile. Please contact the administrator.')
        return redirect('academics:course_list')
    
    # Check if already enrolled
    existing = Enrollment.objects.filter(
        student=student_profile,
        course=course,
        semester=semester
    ).first()
    
    if existing:
        messages.warning(request, f'You are already enrolled in {course.code}.')
        return redirect('academics:course_list')
    
    # Check capacity
    if course.is_full:
        messages.error(request, f'{course.code} is full.')
        return redirect('academics:course_list')
    
    # Check prerequisites
    failed = []
    for prereq in course.prerequisites.all():
        has_passed = Enrollment.objects.filter(
            student=student_profile,
            course=prereq,
            status='APPROVED',
            grade__in=['A', 'B', 'C', 'D', 'P']
        ).exists()
        if not has_passed:
            failed.append(prereq)
    
    if failed:
        prereq_codes = ", ".join([c.code for c in failed])
        messages.warning(request, f'Missing prerequisites: {prereq_codes}')
    
    # Check credit limit
    current_credits = Enrollment.objects.filter(
        student=student_profile,
        semester=semester,
        status='APPROVED'
    ).aggregate(total=Sum('course__credit_units'))['total'] or 0
    
    max_credits = Enrollment.MAX_CREDIT_UNITS
    if current_credits + course.credit_units > max_credits:
        messages.error(
            request, 
            f'Registering for {course.code} would exceed the {max_credits} credit limit. Current: {current_credits}'
        )
        return redirect('academics:course_list')
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        student=student_profile,
        course=course,
        semester=semester,
        status=Enrollment.Status.PENDING
    )
    
    messages.success(request, f'Course {course.code} registration submitted! Pending approval.')
    return redirect('enrollment:my_courses')


@student_required
@transaction.atomic
def drop_course(request, enrollment_id):
    """Drop a course"""
    enrollment = get_object_or_404(
        Enrollment,
        pk=enrollment_id,
        student=request.user.student_profile
    )
    
    if enrollment.status != Enrollment.Status.APPROVED:
        messages.error(request, 'Cannot drop a non-approved enrollment.')
    if enrollment.status != Enrollment.Status.APPROVED:
        messages.error(request, 'Cannot drop a non-approved enrollment.')
        return redirect('dashboard')
    
    enrollment.status = Enrollment.Status.DROPPED
    enrollment.date_dropped = timezone.now()
    enrollment.save()
    
    messages.success(request, f'Course {enrollment.course.code} dropped.')
    return redirect('dashboard')


@student_required
def my_courses(request):
    """View student's enrolled courses"""
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'You do not have a student profile.')
        return redirect('academics:course_list')
    
    enrollments = Enrollment.objects.filter(
        student=student_profile
    ).select_related('course', 'semester')
    
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'enrollment/my_courses.html', context)
