# Generated by Django 4.2.4 on 2023-12-22 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_quiz_author_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='author_id',
            new_name='author',
        ),
    ]
