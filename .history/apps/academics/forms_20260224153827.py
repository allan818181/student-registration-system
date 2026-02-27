from django import forms
from .models import Programme, Course, Semester


class ProgrammeForm(forms.ModelForm):
    """Form for creating/editing programmes"""
    
    class Meta:
        model = Programme
        fields = ['name', 'code', 'duration_years', 'department', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CourseForm(forms.ModelForm):
    """Form for creating/editing courses"""
    
    class Meta:
        model = Course
        fields = [
            'code', 'title', 'description', 'credit_units', 'capacity',
