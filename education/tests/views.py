from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group, User


def get_group(req):
    if req.POST['role'] == 'S':
        group, created = Group.objects.get_or_create(name='student_group')
        return group
    elif req.POST['role'] == 'T':
        group, created = Group.objects.get_or_create(name='teacher_group')
        return group


# Create your views here.
def home(request):
    user = request.user
    is_student = user.groups.filter(name='student_group').exists()
    is_teacher = user.groups.filter(name='teacher_group').exists()

    context = {
        'user': user,
        'is_student': is_student,
        'is_teacher': is_teacher,
    }

    return render(request, 'tests/home.html', context=context)


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add user to a group
            group = get_group(request)
            user.groups.add(group)

            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})
