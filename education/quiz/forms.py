from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Quiz, Answer


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


class CreateQuizForm(forms.Form):
    title = forms.CharField(label='Title', max_length=700)
    description = forms.CharField(widget=forms.Textarea, max_length=2000)

    def save(self):
        data = self.cleaned_data
        model_quiz = Quiz(**data)
        model_quiz.save()

        return model_quiz


class Question(forms.Form):
    pass


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'


class MyDynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields = kwargs.pop('dynamic_fields', [])
        super(MyDynamicForm, self).__init__(*args, **kwargs)

        for name, value in dynamic_fields:
            self.fields[name] = forms.CharField(max_length=100)
