from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('create_quiz', views.create_quiz, name='create_quiz'),
    path('quiz_filling/<int:quiz_id>/question/<int:number_of_question>', views.add_question, name='add_question'),
    path('quiz_filling/<int:quiz_id>', views.quiz_filling, name='quiz_filling'),
    path('my_quizzes', views.my_quizzes, name='my_quizzes'),
    path('quiz/<int:quiz_id>', views.quiz, name='quiz'),
    path('quiz/<int:quiz_id>/question/<int:question_num>', views.question, name='question'),
    path('filtered_quizzes', views.filtered_quizzes, name='filtered_quizzes'),
    path('quiz_taking/<int:quiz_id>/question/<int:question_num>', views.student_answer, name='student_answer'),
    path('quiz_result/<int:quiz_id>', views.quiz_result, name='quiz_result'),
    path('completed_quizzes', views.completed_quizzes, name='completed_quizzes'),
    # path('kakayata_ajax', views.kakayata_ajax, name='kakayata_ajax'),
]
