from rest_framework import serializers
from .models import Category, Item, Question, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, write_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question


class ItemSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, write_only=True, required=False)
    category = serializers.IntegerField(write_only=True)
    class Meta:
        model = Item
        fields = ['id', 'title', 'subtitle', 'button_label', 'access_mode', 'item_type', 'questions', 'category']

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        category = Category.objects.get(id=category_id)
        # questions_data = validated_data.pop('questions')
        item = Item.objects.create(category=category, **validated_data)
        # for question_data in questions_data:
        #     options_data = question_data.pop('options')
        #     question = Question.objects.create(item=item, **question_data)
        #     for option_data in options_data:
        #         Option.objects.create(question=question, **option_data)
        return item


class CategorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Category
        fields = ['id', 'title', 'category_type', 'items']

    def create(self, validated_data):
        # items_data = validated_data.pop('items')
        category = Category.objects.create(**validated_data)
        # for item_data in items_data:
        #     questions_data = item_data.pop('questions')
        #     item = Item.objects.create(category=category, **item_data)
        #     for question_data in questions_data:
        #         options_data = question_data.pop('options')
        #         question = Question.objects.create(item=item, **question_data)
        #         for option_data in options_data:
        #             Option.objects.create(question=question, **option_data)
        return category
