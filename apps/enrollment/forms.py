from django import forms
from .models import Enrollment


class EnrollmentForm(forms.ModelForm):
    """Form for creating enrollment requests"""
    
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'semester']
        widgets = {
            'student': forms.TextInput(attrs={'placeholder': 'Search student...'}),
            'course': forms.TextInput(attrs={'placeholder': 'Search course...'}),
        }


class EnrollmentApprovalForm(forms.ModelForm):
    """Form for approving/rejecting enrollments"""
    
    class Meta:
        model = Enrollment
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Rejection reason or notes...'}),
        }


class GradeForm(forms.ModelForm):
    """Form for assigning grades to enrollments"""
    
    class Meta:
        model = Enrollment
        fields = ['grade']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-select'}),
        }


class CourseRegistrationForm(forms.Form):
    """Form for student course registration"""
    
    course = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Course"
    )
    
    def __init__(self, *args, **kwargs):
        programme_id = kwargs.pop('programme_id', None)
        semester_id = kwargs.pop('semester_id', None)
        super().__init__(*args, **kwargs)
        
        from apps.academics.models import Course
        courses = Course.objects.filter(is_active=True)
        
        if programme_id:
            courses = courses.filter(programme_id=programme_id)
        if semester_id:
            courses = courses.filter(semester=semester_id)
        
        self.fields['course'].queryset = courses


class EnrollmentFilterForm(forms.Form):
    """Form for filtering enrollments"""
    
    STATUS_CHOICES = [('', 'All Statuses')] + list(Enrollment.Status.choices)
    GRADE_CHOICES = [('', 'All Grades')] + list(Enrollment.Grade.choices)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    semester = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Semesters",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.academics.models import Semester
        self.fields['semester'].queryset = Semester.objects.all()
