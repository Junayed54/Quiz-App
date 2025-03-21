from django.contrib import admin
from .models import *


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_questions', 'negative_marking', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'total_questions')
    
    def save_model(self, request, obj, form, change):
        """Automatically update the total_questions field before saving."""
        obj.total_questions = obj.calculate_total_questions()
        super().save_model(request, obj, form, change)
        
        
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category_type', 'access_mode')
    search_fields = ('title', 'category_type')
    list_filter = ('category_type',)
    ordering = ('title',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'access_mode', 'item_type')
    search_fields = ('title', 'subtitle', 'item_type')
    list_filter = ('access_mode', 'item_type', 'category')
    autocomplete_fields = ('category',)
    ordering = ('title',)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    fields = ('option_text', 'is_correct')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'item')
    search_fields = ('question_text',)
    list_filter = ('item__category',)
    autocomplete_fields = ('item',)
    inlines = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'option_text', 'is_correct', 'question')
    search_fields = ('option_text', 'question__question_text')
    list_filter = ('is_correct',)
    autocomplete_fields = ('question',)
    ordering = ('question', 'option_text')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'total_questions', 'correct_answers', 'wrong_answers', 'score', 'attempt_date')
    list_filter = ('attempt_date', 'item', 'user')
    search_fields = ('user__username', 'item__title')
    readonly_fields = ('attempt_date', 'score')
    
    def has_add_permission(self, request):
        """Prevent manual addition of quiz attempts."""
        return False