from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EnrollmentManager(models.Manager):
    """Custom manager for Enrollment model"""
    
    def approved(self):
        return self.filter(status=self.model.Status.APPROVED)
    
    def pending(self):
        return self.filter(status=self.model.Status.PENDING)
    
    def dropped(self):
        return self.filter(status=self.model.Status.DROPPED)


class Enrollment(models.Model):
    """
    Core model for course registration.
    Represents a student's enrollment in a specific course for a specific semester.
    
    This is the heart of the student registration system.
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        DROPPED = 'DROPPED', _('Dropped')
        REJECTED = 'REJECTED', _('Rejected')
    
    class Grade(models.TextChoices):
        A = 'A', _('A - Excellent')
        B = 'B', _('B - Very Good')
        C = 'C', _('C - Good')
        D = 'D', _('D - Pass')
        F = 'F', _('F - Fail')
        P = 'P', _('P - Pass (Pass/Fail)')
        I = 'I', _('I - Incomplete')
        W = 'W', _('W - Withdrawn')
    
    # Maximum credit units per semester
    MAX_CREDIT_UNITS = 18
    
    student = models.ForeignKey(
        'accounts.StudentProfile',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text=_('Enrolled student')
    )
    
    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text=_('Course being enrolled in')
    )
    
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text=_('Semester of enrollment')
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_('Enrollment status')
    )
    
    grade = models.CharField(
        max_length=2,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text=_('Final grade (if completed)')
    )
    
    date_registered = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When enrollment was requested')
    )
    
    date_approved = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When enrollment was approved')
    )
    
    date_dropped = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When enrollment was dropped')
    )
    
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_enrollments',
        help_text=_('Admin who approved this enrollment')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Additional notes (rejection reason, etc.)')
    )
    
    objects = EnrollmentManager()
    
    class Meta:
        db_table = 'enrollments'
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        ordering = ['-date_registered']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course', 'semester'],
                name='unique_enrollment'
            )
        ]
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.course.code} ({self.semester})"
    
    def clean(self):
        """Validate enrollment business rules"""
        if self.status == self.Status.APPROVED:
            # Check capacity
            approved_count = Enrollment.objects.filter(
                course=self.course,
                semester=self.semester,
                status=self.Status.APPROVED
            ).exclude(pk=self.pk).count()
            
            if approved_count >= self.course.capacity:
                raise ValidationError(
                    _('Course is full. Cannot enroll.')
                )
            
            # Check credit limit
            total_credits = Enrollment.objects.filter(
                student=self.student,
                semester=self.semester,
                status=self.Status.APPROVED
            ).exclude(pk=self.pk).aggregate(
                total=models.Sum('course__credit_units')
            )['total'] or 0
            
            if total_credits + self.course.credit_units > self.MAX_CREDIT_UNITS:
                raise ValidationError(
                    _('Maximum credit units ({max}) would be exceeded. '
                      'Current: {current}, Course: {course}').format(
                        max=self.MAX_CREDIT_UNITS,
                        current=total_credits,
                        course=self.course.credit_units
                    )
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED
    
    @property
    def is_pending(self):
        return self.status == self.Status.PENDING
    
    @property
    def is_dropped(self):
        return self.status == self.Status.DROPPED
    
    def check_prerequisites(self):
        """
        Check if student has passed all prerequisites.
        Returns tuple (passed: bool, failed_prerequisites: list)
        """
        failed = []
        for prereq in self.course.prerequisites.all():
            passed = Enrollment.objects.filter(
                student=self.student,
                course=prereq,
                status=self.Status.APPROVED,
                grade__in=['A', 'B', 'C', 'D', 'P']
            ).exists()
            if not passed:
                failed.append(prereq)
        return (len(failed) == 0, failed)
