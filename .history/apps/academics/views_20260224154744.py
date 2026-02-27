from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Programme, Course, Semester
from .forms import ProgrammeForm, CourseForm, SemesterForm, CourseSearchForm
from apps.accounts.decorators import admin_required, role_required


def course_list(request):
    """List all available courses with filtering"""
    courses = Course.objects.filter(is_active=True).select_related('programme', 'lecturer')
    
    # Apply filters
    search = request.GET.get('search', '')
    programme_id = request.GET.get('programme', '')
    semester_filter = request.GET.get('semester', '')
    
    if search:
        courses = courses.filter(
            Q(code__icontains=search) | Q(title__icontains=search)
        )
    
    if programme_id:
        courses = courses.filter(programme_id=programme_id)
    
    if semester_filter:
        courses = courses.filter(semester=semester_filter)
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'programmes': Programme.objects.filter(is_active=True),
        'semesters': range(1, 7),
        'search': search,
        'programme_id': programme_id,
        'semester_filter': semester_filter,
    }
    return render(request, 'academics/course_list.html', context)


def course_detail(request, pk):
    """Show course details"""
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'academics/course_detail.html', {'course': course})


@admin_required
def course_create(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('academics:course_list')
    else:
        form = CourseForm()
    
    return render(request, 'academics/course_form.html', {'form': form, 'action': 'Create'})


@admin_required
def course_edit(request, pk):
    """Edit an existing course"""
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('academics:course_list')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'academics/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


def programme_list(request):
    """List all programmes"""
    programmes = Programme.objects.filter(is_active=True)
    return render(request, 'academics/programme_list.html', {'programmes': programmes})


@admin_required
def programme_create(request):
    """Create a new programme"""
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programme created successfully!')
            return redirect('academics:programme_list')
    else:
        form = ProgrammeForm()
    
    return render(request, 'academics/programme_form.html', {'form': form, 'action': 'Create'})


def semester_list(request):
    """List all semesters"""
    semesters = Semester.objects.all().order_by('-year', '-term')
    return render(request, 'academics/semester_list.html', {'semesters': semesters})


@admin_required
def semester_create(request):
    """Create a new semester"""
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semester created successfully!')
            return redirect('academics:semester_list')
    else:
        form = SemesterForm()
    
    return render(request, 'academics/semester_form.html', {'form': form, 'action': 'Create'})

