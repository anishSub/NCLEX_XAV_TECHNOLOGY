from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Users

# Custom Signup Form (Uses Email instead of Username)
class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ('email', 'username', 'first_name', 'last_name')
        # We don't need to add 'role' here because your model automatically 
        # sets it to 'STUDENT' in the save() method.

# Custom Login Form (just to style it later if needed)
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))