from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import RegisterForm, CreateQuizForm, AnswerForm, MyDynamicForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from .models import Quiz, Question, TypeOfQuestion, Answer, Score
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models import Max, Exists, Q
from django.shortcuts import get_object_or_404
import django.views.defaults

def get_group_for_registration(req):
    def create_group_with_permissions(group, permissions_list):
        for permission_code in permissions_list:
            action, model = permission_code.split('_')
            content_type = ContentType.objects.get(app_label='quiz', model=model)

            permission = Permission.objects.get(content_type=content_type, codename=permission_code)
            group.permissions.add(permission)

    if req.POST['role'] == 'S':
        group, created = Group.objects.get_or_create(name='student_group')
        if created:
            # Add permissions to student_group
            permissions = [
                'view_answer',
                'view_question',
                'view_quiz',
            ]
            create_group_with_permissions(group, permissions)
        return group
    elif req.POST['role'] == 'T':
        group, created = Group.objects.get_or_create(name='teacher_group')
        if created:
            # Add permissions to teacher_group
            permissions = [
                'add_answer',
                'change_answer',
                'delete_answer',
                'view_answer',
                'add_question',
                'change_question',
                'delete_question',
                'view_question',
                'add_quiz',
                'change_quiz',
                'delete_quiz',
                'view_quiz',
            ]
            create_group_with_permissions(group, permissions)
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
# @permission_required(perm='add_quiz', raise_exception=True)
def create_quiz(request):
    if request.method == 'POST':
        form = CreateQuizForm(request.POST)
        if form.is_valid():
            form.cleaned_data['author'] = request.user

            # save to the database
            quiz = form.save()

            uri = reverse('quiz_filling', args=(quiz.id,))
            return redirect(uri)
    else:
        form = CreateQuizForm()
    context = {
        'form': form,
        'user': request.user,
    }

    context.update(get_group(request))

    return render(request, 'quiz/create_quiz.html', context=context)


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


def my_quizzes(request):
    quizzes = Quiz.objects.filter(author=request.user)
    context = {
        'quizzes': quizzes,
    }
    context.update(get_group(request))
    return render(request, 'quiz/list_of_quizzes.html', context=context)


def quiz(request, quiz_id):
    quiz_object = get_object_or_404(Quiz, id=quiz_id)
    if request.user.groups.filter(name='student_group').exists():
        student_already_taken_the_test = Score.objects.filter(
            related_quiz=quiz_object,
            related_student=request.user
        ).exists()
        if student_already_taken_the_test:
            uri = reverse('quiz_result', args=(quiz_id,))
            return redirect(uri)

        context = {
            'quiz_object': quiz_object,
        }
        context.update(get_group(request))
        return render(request, 'quiz/quiz_object_for_student.html', context=context)
    elif request.user.groups.filter(name='teacher_group').exists():
        questions = Question.objects.filter(related_quiz=quiz_object)
        context = {
            'quiz_object': quiz_object,
            'questions': questions,
        }
        context.update(get_group(request))
        return render(request, 'quiz/quiz_object.html', context=context)


def question(request, quiz_id, question_num):
    question_object = get_object_or_404(
        Question,
        question_number=question_num,
        related_quiz__id=quiz_id)
    options = Answer.objects.filter(related_question=question_object)

    context = {
        'question': question_object,
        'options': options,
    }
    context.update(get_group(request))
    return render(request, 'quiz/question_object.html', context=context)


def filtered_quizzes(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        quizzes = Quiz.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(author__username__icontains=search_query))
    else:
        quizzes = Quiz.objects.all()

    context = {
        'quizzes': quizzes,
    }
    context.update(get_group(request))
    return render(request, 'quiz/filtered_quizzes.html', context=context)


def student_answer(request, quiz_id, question_num):
    quiz_object = get_object_or_404(Quiz, id=quiz_id)
    question_object = get_object_or_404(
        Question,
        related_quiz=quiz_object,
        question_number=question_num
    )
    answer_options = Answer.objects.filter(related_question=question_object)
    count_of_questions_in_the_quiz = Question.objects.filter(related_quiz=quiz_object).count()

    if request.method == 'POST':
        user_score_of_the_quiz, created = Score.objects.get_or_create(
            related_quiz=quiz_object,
            related_student=request.user
        )
        question_type = question_object.question_type.question_type_name
        checked_answers = [request.POST[option] for option in request.POST if 'choice' in option]
        correct_answers = [answer.text_of_answer for answer in answer_options if answer.is_answer_right]

        if sorted(checked_answers) == sorted(correct_answers):
            user_score_of_the_quiz.add_score(1)
            user_score_of_the_quiz.save()
        if question_object.question_number == count_of_questions_in_the_quiz:
            uri = reverse('quiz_result', args=(quiz_id,))
            return redirect(uri)
        else:
            uri = reverse('student_answer', args=(quiz_id, (question_num + 1)))
            return redirect(uri)

    form_action = reverse('student_answer', args=(quiz_id, question_num))
    context = {
        'quiz': quiz_object,
        'question': question_object,
        'answer_options': answer_options,
        'question_type': question_object.question_type.question_type_name,
        'form_action': form_action,
    }
    context.update(get_group(request))
    return render(request, 'quiz/student_answer.html', context=context)


def quiz_result(request, quiz_id):
    user = request.user
    quiz_object = Quiz.objects.get(id=quiz_id)
    total_questions_in_quiz = Question.objects.filter(related_quiz=quiz_object).count()
    score_result = Score.objects.get(
        related_quiz=quiz_object,
        related_student=user
    )

    context = {
        'total_questions': total_questions_in_quiz,
        'score_result': score_result,
    }
    context.update(get_group(request))
    return render(request, 'quiz/quiz_result.html', context=context)


def completed_quizzes(request):
    if request.user.groups.filter(name='student_group').exists():
        results = (Score.objects.filter(related_student=request.user)
                   .select_related('related_quiz'))
        context = {
            'results': results,
        }
        context.update(get_group(request))
        return render(request, 'quiz/completed_quizzes.html', context=context)

    elif request.user.groups.filter(name='teacher_group').exists():
        results = (Score.objects.
                   select_related('related_quiz').
                   filter(related_quiz__author=request.user))
        context = {
            'results': results,
        }
        context.update(get_group(request))
        return render(request, 'quiz/list_of_completed_quizzes_for_teacher.html', context=context)


def handler404(request, exception):
    context = {}
    context.update(get_group(request))
    return render(request, 'quiz/404.html', context=context, status=404)
