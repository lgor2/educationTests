from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Question


@receiver(post_save, sender=Question)
def update_quiz_question_count(sender, instance, **kwargs):
    quiz = instance.related_quiz
    quiz.question_count = Question.objects.filter(related_quiz=quiz).count()
    print("Signals", quiz.question_count)
    quiz.save()


@receiver(post_delete, sender=Question)
def update_quiz_question_count_on_delete(sender, instance, **kwargs):
    quiz = instance.related_quiz
    quiz.question_count = Question.objects.filter(related_quiz=quiz).count()
    quiz.save()
