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
            'fields': ('description', 'is_active')
        }),
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    """Admin configuration for Semester model"""
    
    list_display = ['__str__', 'year', 'term', 'is_active', 'registration_start', 'registration_end']
    list_filter = ['is_active', 'year']
    search_fields = ['year', 'term']
    ordering = ['-year', '-term']
    
    fieldsets = (
        ('Academic Period', {
            'fields': ('year', 'term')
        }),
        ('Registration', {
            'fields': ('is_active', 'registration_start', 'registration_end')
        }),
    )
    
    actions = ['set_active_semester']
    
    def set_active_semester(self, request, queryset):
        for semester in queryset:
            semester.is_active = True
            semester.save()
    set_active_semester.short_description = 'Set selected semester as active'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model"""
    
    list_display = ['code', 'title', 'programme', 'semester', 'credit_units', 'capacity', 'lecturer', 'is_active']
    list_filter = ['is_active', 'semester', 'programme']
    search_fields = ['code', 'title', 'description']
    ordering = ['code']
    raw_id_fields = ['lecturer', 'prerequisites']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('code', 'title', 'description')
        }),
        ('Academic Details', {
            'fields': ('programme', 'semester', 'credit_units', 'capacity')
        }),
        ('Assignment', {
            'fields': ('lecturer', 'prerequisites')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    filter_horizontal = ['prerequisites']
