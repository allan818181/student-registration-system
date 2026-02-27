from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Enrollment model"""
    
    list_display = ['student', 'course', 'semester', 'status', 'grade', 'date_registered']
    list_filter = ['status', 'semester', 'grade']
    search_fields = [
        'student__registration_number',
        'student__user__first_name',
        'student__user__last_name',
        'course__code',
        'course__title'
    ]
    ordering = ['-date_registered']
    raw_id_fields = ['student', 'course', 'semester', 'approved_by']
    
    fieldsets = (
        ('Enrollment Details', {
            'fields': ('student', 'course', 'semester')
        }),
        ('Status & Grade', {
            'fields': ('status', 'grade')
        }),
        ('Timestamps', {
            'fields': ('date_registered', 'date_approved', 'date_dropped')
        }),
        ('Approval', {
            'fields': ('approved_by', 'notes')
        }),
    )
    
    readonly_fields = ['date_registered', 'date_approved', 'date_dropped']
    
    actions = ['approve_enrollments', 'drop_enrollments']
    
    def approve_enrollments(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=Enrollment.Status.APPROVED,
            date_approved=timezone.now()
        )
        self.message_user(request, f'{updated} enrollment(s) approved.')
    approve_enrollments.short_description = 'Approve selected enrollments'
    
    def drop_enrollments(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=Enrollment.Status.DROPPED,
            date_dropped=timezone.now()
        )
        self.message_user(request, f'{updated} enrollment(s) dropped.')
    drop_enrollments.short_description = 'Drop selected enrollments'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'course', 'semester'
        )
