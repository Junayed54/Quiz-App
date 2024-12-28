from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=200)
    category_type = models.CharField(max_length=100, choices=[
        ('default', 'Default'),
        ('regular_quiz', 'Regular Quiz'),
        ('practice', 'Practice'),
        ('reading', 'Reading'),
    ])
    
    def __str__(self):
        return self.title


class Item(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    button_label = models.CharField(max_length=50, default='Play')
    access_mode = models.CharField(max_length=50, choices=[
        ('public', 'Public'),
        ('private', 'Private'),
    ], default='public')
    item_type = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title


class Question(models.Model):
    question_text = models.TextField()
    item = models.ForeignKey(Item, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text


class Option(models.Model):
    option_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)

    def __str__(self):
        return self.option_text
