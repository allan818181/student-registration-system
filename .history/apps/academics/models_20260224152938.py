from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Programme(models.Model):
    """
    Represents a degree or certificate program.
    Example: Bachelor of Computer Science, Diploma in IT
    """
    
    DURATION_CHOICES = [(i, f'{i} Year{"s" if i > 1 else ""}') for i in range(1, 7)]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text=_('Full programme name')
    )
    
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text=_('Short programme code (e.g., BCS, DIT)')
    )
    
    duration_years = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        default=3,
        help_text=_('Programme duration in years')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Programme description and details')
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Department offering the programme')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether programme is currently active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'programmes'
        verbose_name = _('Programme')
        verbose_name_plural = _('Programmes')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    """
    Represents an academic semester/term.
    Example: 2026 Semester 1, 2026 Semester 2
    """
    
    TERM_CHOICES = [
        (1, _('Semester 1')),
        (2, _('Semester 2')),
        (3, _('Semester 3 (Summer)')),
    ]
    
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)],
        help_text=_('Academic year')
    )
    
    term = models.PositiveIntegerField(
        choices=TERM_CHOICES,
        help_text=_('Term number within the year')
    )
    
    is_active = models.BooleanField(
        default=False,
        help_text=_('Current active semester for registrations')
    )
    
    registration_start = models.DateField(
        null=True,
        blank=True,
        help_text=_('Course registration start date')
    )
    
    registration_end = date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Course registration end date')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'semesters'
        verbose_name = _('Semester')
        verbose_name_plural = _('Semesters')
        ordering = ['-year', '-term']
        unique_together = ['year', 'term']
    
    def __str__(self):
        return f"{self.year} - Semester {self.term}"
    
    def save(self, *args, **kwargs):
        # If this semester is being set as active, deactivate others
        if self.is_active:
            Semester.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Represents a course/unit within a programme.
    """
    
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 7)]
    
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text=_('Course code (e.g., CS101)')
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Course title')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Course description')
    )
    
    credit_units = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text=_('Credit units for this course')
    )
    
    capacity = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text=_('Maximum number of students')
    )
    
    semester = models.PositiveIntegerField(
        choices=SEMESTER_CHOICES,
        default=1,
        help_text=_('Semester in which course is offered')
    )
    
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='courses',
        help_text=_('Programme this course belongs to')
    )
    
    lecturer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_courses',
        limit_choices_to={'role': 'LECTURER'},
        help_text=_('Assigned lecturer')
    )
    
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='prerequisite_for',
        help_text=_('Courses that must be completed before taking this one')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether course is currently active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    @property
    def current_enrollment(self):
        """Get current number of enrolled students"""
        return self.enrollments.filter(status='APPROVED').count()
    
    @property
    def is_full(self):
        """Check if course has reached capacity"""
        return self.current_enrollment >= self.capacity
    
    @property
    def available_seats(self):
        """Get number of available seats"""
        return max(0, self.capacity - self.current_enrollment)
