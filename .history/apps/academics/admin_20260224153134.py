from django.contrib import admin
from .models import Programme, Semester, Course


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    """Admin configuration for Programme model"""
    
    list_display = ['code', 'name', 'duration_years', 'department', 'is_active']
    list_filter = ['is_active', 'duration_years', 'department']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'duration_years', 'department')
        }),
        ('Details', {
