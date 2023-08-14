from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('S', 'Student'),
        ('T', 'Teacher'),
    ]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Select your role.', initial='S')

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]
