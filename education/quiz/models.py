from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Quiz(models.Model):
    title = models.CharField(max_length=700)
    description = models.CharField(max_length=2000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.title

    def get_id_question(self, num):
        obj = Question.objects.filter(Q(related_quiz=self), Q(question_number=num))[0]
        return obj.id

class TypeOfQuestion(models.Model):
    question_type_name = models.CharField(max_length=500)

    def __str__(self):
        return self.question_type_name


class Question(models.Model):
    question_number = models.IntegerField(verbose_name='Index of the question in the quiz')
    text = models.CharField(max_length=1000)
    related_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_type = models.ForeignKey(TypeOfQuestion, on_delete=models.CASCADE)

    def __str__(self):
        return str((self.text, self.related_quiz))


class Answer(models.Model):
    answer_number = models.IntegerField(verbose_name='Index of the answer in the question')
    is_answer_right = models.BooleanField(verbose_name='Is answer right')
    text_of_answer = models.CharField(
        verbose_name='Text of the answer',
        max_length=1000,
    )
    related_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str((self.answer_number, self.is_answer_right, self.text_of_answer))


class Score(models.Model):
    related_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    related_student = models.ForeignKey(User, on_delete=models.CASCADE)
    score_counter = models.IntegerField(verbose_name='User rating for the quiz', default=0)

    def add_score(self, number_of_points=1):
        self.score_counter += number_of_points

    def __str__(self):
        return str(self.score_counter)
