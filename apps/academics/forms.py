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
            'semester', 'programme', 'lecturer', 'prerequisites', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'prerequisites': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter lecturers to only show users with lecturer role
        from apps.accounts.models import User
        self.fields['lecturer'].queryset = User.objects.filter(role=User.Role.LECTURER)


class SemesterForm(forms.ModelForm):
    """Form for creating/editing semesters"""
    
    class Meta:
        model = Semester
        fields = ['year', 'term', 'is_active', 'registration_start', 'registration_end']
        widgets = {
            'registration_start': forms.DateInput(attrs={'type': 'date'}),
            'registration_end': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('registration_start')
        end = cleaned_data.get('registration_end')
        
        if start and end and end < start:
            raise forms.ValidationError("End date must be after start date")
        
        return cleaned_data


class CourseSearchForm(forms.Form):
    """Form for searching courses"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by code or title...',
            'class': 'form-control'
        })
    )
    
    programme = forms.ModelChoiceField(
        queryset=Programme.objects.all(),
        required=False,
        empty_label="All Programmes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semester = forms.ChoiceField(
        choices=[('', 'All Semesters')] + list(Course.SEMESTER_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
