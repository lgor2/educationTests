from django.shortcuts import render, redirect
from .forms import RegisterForm, CreateQuizForm, AnswerForm, MyDynamicForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, permission_required
from .models import Quiz, Question, TypeOfQuestion, Answer
from django.forms import formset_factory
from django.http import JsonResponse
from django.db.models import Max, Exists


def get_group_for_registration(req):
    if req.POST['role'] == 'S':
        group, created = Group.objects.get_or_create(name='student_group')
        return group
    elif req.POST['role'] == 'T':
        group, created = Group.objects.get_or_create(name='teacher_group')
        return group


def get_group(req):
    is_student = req.user.groups.filter(name='student_group').exists()
    is_teacher = req.user.groups.filter(name='teacher_group').exists()

    context = {
        'is_student': is_student,
        'is_teacher': is_teacher,
    }

    return context


# Create your views here.
def home(request):
    user = request.user

    context = {
        'user': user,
    }

    student_or_teacher = get_group(request)
    context.update(student_or_teacher)

    return render(request, 'quiz/home.html', context=context)


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add user to a group
            group = get_group_for_registration(request)
            user.groups.add(group)

            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})


@login_required(login_url='login/')
# @permission_required()
def create_quiz(request):
    if request.method == 'POST':
        form = CreateQuizForm(request.POST)
        if form.is_valid():
            # save to the database and extract quiz_id
            quiz = form.save()

            quiz_id = quiz.id
            return redirect(f'/quiz_filling/{quiz_id}')
    else:
        form = CreateQuizForm()
    context = {
        'form': form,
        'user': request.user,
    }

    context.update(get_group(request))

    return render(request, 'quiz/create_quiz.html', context=context)


def kakayata_ajax(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax and request.method == 'POST':

        # data = {'1': 'Hello world'}
        # return JsonResponse(data, status=200)

        context = {'text': 'Hello, world!'}

        return render(request, 'quiz/testajax.html', context=context)


@login_required(login_url='login/')
def quiz_filling(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)

    questions = Question.objects.filter(related_quiz=quiz)

    if questions.exists():
        max_question_number = questions.aggregate(Max('question_number'))['question_number__max']
        number_of_question = max_question_number + 1
        print(f'max number of question = {number_of_question}')
    else:
        number_of_question = 1

    context = {
        'quiz': quiz,
        'quiz_id': quiz_id,
        'user': request.user,
        'number_of_question': number_of_question,
    }

    context.update(get_group(request))

    return render(request, 'quiz/quiz_filling.html', context=context)


@login_required(login_url='login/')
def add_question(request, quiz_id, number_of_question):
    if request.method == 'POST':
        post_data = request.POST
        question_type = post_data.get('question_type')

        form = MyDynamicForm(request.POST, dynamic_fields=request.POST.items())

        if question_type == 'open':
            if post_data.get('open_question', False):
                question_text = post_data['open_question']
            if post_data.get('open_answer', False):
                answer_text = post_data['open_answer']

            question = Question(
                question_number=number_of_question,
                text=question_text,
                related_quiz=Quiz.objects.get(id=quiz_id),
                question_type=TypeOfQuestion.objects.get(question_type_name='open'),
            )
            question.save()

            answer = Answer(
                answer_number=1,
                is_answer_right=True,
                text_of_answer=answer_text,
                related_question=question,
            )
            answer.save()

        elif question_type == 'close_one':
            if post_data.get('close_one_question', False):
                question_text = post_data['close_one_question']

            question = Question(
                question_number=number_of_question,
                text=question_text,
                related_quiz=Quiz.objects.get(id=quiz_id),
                question_type=TypeOfQuestion.objects.get(question_type_name='close_one'),
            )
            question.save()

            answer_input = post_data.get('close_one_checkbox_answer', False)

            dict_of_answer_options = dict()

            for i in post_data:
                if 'close_one_answer_' in i:
                    number_of_answer_option = i.split('_')[-1]
                    dict_of_answer_options[number_of_answer_option] = post_data[i]
                    is_answer_right = False

                    if answer_input == i:
                        is_answer_right = True

                    answer = Answer(
                        answer_number=number_of_answer_option,
                        is_answer_right=is_answer_right,
                        text_of_answer=post_data[i],
                        related_question=question,
                    )
                    answer.save()

        elif question_type == 'close_many':
            if post_data.get('close_many_question', False):
                question_text = post_data['close_many_question']

            question = Question(
                question_number=number_of_question,
                text=question_text,
                related_quiz=Quiz.objects.get(id=quiz_id),
                question_type=TypeOfQuestion.objects.get(question_type_name='close_many'),
            )
            question.save()

            dict_of_answer_options = dict()
            list_of_right_answer_options = list()
            for i in post_data:
                if 'close_many_answer_' in i:
                    is_answer_right = False
                    if len(post_data.getlist(i)) == 2:
                        list_of_right_answer_options.append(i.split('_')[-1])
                        is_answer_right = True
                    number_of_answer_option = i.split('_')[-1]
                    dict_of_answer_options[number_of_answer_option] = post_data[i]

                    answer = Answer(
                        answer_number=number_of_answer_option,
                        is_answer_right=is_answer_right,
                        text_of_answer=post_data[i],
                        related_question=question,
                    )
                    answer.save()

        else:
            pass

        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(related_quiz=quiz)
        context = {
            'quiz': quiz,
            'quiz_id': quiz_id,
            'user': request.user,
            'number_of_question': number_of_question+1,
            'questions': questions,
        }
        context.update(get_group(request))
        return render(request, 'quiz/quiz_filling.html', context=context)

    quiz = Quiz.objects.get(id=quiz_id)
    context = {}
    context.update(get_group(request))
    return render(request, 'quiz/assessments.html', context=context)


@login_required('/login')
def list_of_quizzes(request):

    context = {}
    context.update(get_group(request))
    return render(request, 'quiz/list_of_quizzes.html', context=context)
