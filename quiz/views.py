from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Category, Item, Question, Option
from .serializers import CategorySerializer, ItemSerializer

class CategoryCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize the data
        serializer = CategorySerializer(data=request.data)
        
        # Check if the data is valid
        if serializer.is_valid():
            category = serializer.save()  # Save the category
            return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
        
        # If invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize the data for Item creation
        serializer = ItemSerializer(data=request.data)
        
        # Check if the data is valid
        if serializer.is_valid():
            item = serializer.save()  # Save the item
            return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
        
        # If invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class GetQuestionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        category_id = request.data.get('category_id')
        item_id = request.data.get('item_id')
        current_question_index = request.data.get('current_question_index', 0)  # Default to the first question
        
        try:
            category = Category.objects.get(id=category_id)
            item = Item.objects.get(id=item_id, category=category)
        except Category.DoesNotExist:
            return Response(
                {"response_type": "error", "is_logged_in": True, "message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Item.DoesNotExist:
            return Response(
                {"response_type": "error", "is_logged_in": True, "message": "Item not found in the specified category."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get questions
        questions = Question.objects.filter(item=item)
        
        if current_question_index < 0 or current_question_index >= len(questions):
            return Response(
                {"response_type": "error", "is_logged_in": True, "message": "Invalid question index."},
                status=status.HTTP_400_BAD_REQUEST
            )

        question = questions[current_question_index]
        options = Option.objects.filter(question=question)
        answer_set = [
            {
                "answer_id": str(option.id),
                "answer": option.option_text,
                "is_ture": option.is_correct
            }
            for option in options
        ]

        # Response for the current question
        return Response(
            {
                "response_type": "success",
                "is_logged_in": True,
                "question": {
                    "question_id": str(question.id),
                    "question": question.question_text,
                    "answer_set": answer_set
                },
                "next_question_index": current_question_index + 1 if current_question_index + 1 < len(questions) else None,
                "is_last_question": current_question_index + 1 >= len(questions)
            },
            status=status.HTTP_200_OK
        )



class DashboardView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # user_auth_token = request.GET.get('user_auth_token')

        # # Validate user authentication token
        # if not user_auth_token:
        #     return Response(
        #         {"response_type": "error", "is_logged_in": False, "message": "Authentication token is missing."},
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )

        # Fetch categories and related items
        categories = Category.objects.all()
        task_category = []

        for category in categories:
            items = Item.objects.filter(category=category)
            task_items = [
                {
                    "item_id": str(item.id),
                    "item_title": item.title,
                    "item_subtitle": item.subtitle,
                    "item_button_label": item.button_label or "Quiz Play",
                    "access_mode": item.access_mode or "public",
                    "item_type": item.item_type or "default",
                }
                for item in items
            ]

            task_category.append({
                "category_id": str(category.id),
                "category_title": category.title,
                "category_type": category.category_type or "default",
                "task_items": task_items,
            })

        # Construct response
        return Response(
            {
                "response_type": "success",
                "is_logged_in": True,
                "task_category": task_category,
            },
            status=status.HTTP_200_OK
        )
        
        
class QuestionUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ensure a file is provided
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse the uploaded Excel file
            df = pd.read_excel(file)

            # Expected columns
            required_columns = [
                'Question', 'Subject', 'Category', 'Options_num', 
                'Option1', 'Option2', 'Option3', 'Option4', 'Answer'
            ]

            if not all(col in df.columns for col in required_columns):
                return Response(
                    {'error': 'Excel file is missing required columns.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():  # Ensure atomicity
                for _, row in df.iterrows():
                    # Retrieve or validate category and subject (assuming Item represents Subject here)
                    category_id = row['Category']
                    subject_id = row['Subject']
                    question_text = row['Question']
                    options_num = int(row['Options_num'])
                    answers = row['Answer'].split(',')  # Expected format: "Option1,Option3"
                    answers = [answer.strip().capitalize() for answer in answers]  # Make sure answers are properly formatted

                    # Fetch or create category and subject
                    category, created = Category.objects.get_or_create(id=category_id)
                    item, created = Item.objects.get_or_create(id=subject_id)

                    # Create or update the question
                    question, created = Question.objects.get_or_create(
                        question_text=question_text,
                        item=item
                    )

                    # Create or update options
                    for i in range(1, options_num + 1):
                        option_text = row.get(f'Option{i}')
                        if option_text:
                            option_text = option_text.capitalize()  # Convert option text to match format (e.g., Option1)
                            is_correct = f'Option{i}'.capitalize() in answers
                            Option.objects.update_or_create(
                                question=question,
                                option_text=option_text,
                                defaults={'is_correct': is_correct}
                            )

            return Response({'message': 'Questions uploaded successfully!'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)