# Generated by Django 5.1.1 on 2025-01-06 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_quiz_negative_marking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizattempt',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]