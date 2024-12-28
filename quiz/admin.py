from django.contrib import admin
from .models import Category, Item, Question, Option


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category_type')
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
