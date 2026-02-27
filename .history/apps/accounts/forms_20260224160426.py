from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import User, StudentProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users with our custom User model"""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True


class UserChangeForm(UserChangeForm):
    """Form for editing existing users"""
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 
                  'phone', 'address', 'date_of_birth', 'profile_picture', 'is_active']


class StudentProfileForm(forms.ModelForm):
    """Form for creating/editing student profiles"""
    
    class Meta:
        model = StudentProfile
        fields = ['user', 'registration_number', 'year_of_study', 'admission_date', 'is_active']
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'user': forms.TextInput(attrs={'placeholder': 'Start typing to search...'})
        }


class StudentRegistrationForm(forms.ModelForm):
    """Combined form for creating a student user and their profile"""
    
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = StudentProfile
        fields = ['registration_number', 'year_of_study', 'admission_date']
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data
    
    def clean_registration_number(self):
        reg_no = self.cleaned_data.get('registration_number')
        if StudentProfile.objects.filter(registration_number=reg_no).exists():
            raise forms.ValidationError("Registration number already exists")
        return reg_no
