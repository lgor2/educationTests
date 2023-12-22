from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('create_quiz', views.create_quiz, name='create_quiz'),
    path('quiz_filling/<int:quiz_id>/question/<int:number_of_question>', views.add_question, name='add_question'),
    path('quiz_filling/<int:quiz_id>', views.quiz_filling, name='quiz_filling'),
    path('kakayata_ajax', views.kakayata_ajax, name='kakayata_ajax'),
]
