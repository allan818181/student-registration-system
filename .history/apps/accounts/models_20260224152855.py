from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    
    Roles:
    - STUDENT: Can view courses and register for courses
    - LECTURER: Can view assigned courses, upload grades, view reports
    - ADMIN: Full system access
    """
    
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        LECTURER = 'LECTURER', _('Lecturer')
        ADMIN = 'ADMIN', _('Admin')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('User role determining system permissions')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Contact phone number')
    )
    
    address = models.TextField(
        blank=True,
        help_text=_('Physical address')
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of birth')
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text=_('User profile picture')
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    @property
    def is_lecturer(self):
        return self.role == self.Role.LECTURER
    
    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class StudentProfile(models.Model):
    """
    Extended profile for student users.
    Links to User model and tracks academic information.
    """
    
    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 7)]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text=_('Associated user account')
    )
    
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Unique student registration number')
    )
    
    year_of_study = models.PositiveIntegerField(
        choices=YEAR_CHOICES,
        default=1,
        help_text=_('Current year of study')
    )
    
    admission_date = models.DateField(
        help_text=_('Date of admission')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether student is currently active')
    )
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')
        ordering = ['registration_number']
    
    def __str__(self):
        return f"{self.registration_number} - {self.user.get_full_name()}"
