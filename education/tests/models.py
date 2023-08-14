from django.db import models


class Student(models.Model):
    pass


class Teacher(models.Model):
    pass


class Test(models.Model):
    title = models.CharField(max_length=500)


class Question(models.Model):
    text = models.CharField(max_length=1000)


class Answer(models.Model):
    text = models.CharField(max_length=500)
