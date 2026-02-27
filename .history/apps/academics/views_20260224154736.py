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
    
