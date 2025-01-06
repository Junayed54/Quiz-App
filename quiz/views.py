from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import *
from .serializers import *





class QuizCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            quiz = serializer.save()
            quiz.calculate_total_questions()  # Calculate total questions after saving
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

# class GetQuestionView(APIView):
#     def get(self, request, question_id=None):
#         # If no question_id is passed, return the first question
#         if not question_id:
#             first_question = Question.objects.first()
#             if not first_question:
#                 return Response({"message": "No questions available"}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({
#                 "question_id": first_question.id,
#                 "question_text": first_question.question_text,
#                 "options": [{"id": option.id, "text": option.option_text} for option in first_question.options.all()],
#             })

#         # Get the current question by question_id
#         try:
#             current_question = Question.objects.get(id=question_id)
#         except Question.DoesNotExist:
#             return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Fetch the next question based on the current question
#         next_question = Question.objects.filter(id__gt=current_question.id).first()
        
#         if next_question:
#             return Response({
#                 "question_id": current_question.id,
#                 "question_text": current_question.question_text,
#                 "options": [{"id": option.id, "text": option.option_text} for option in current_question.options.all()],
#                 "next_question_id": next_question.id,
#             })
#         else:
#             return Response({
#                 "message": "No more questions available",
#                 "quiz_completed": True
#             }, status=status.HTTP_200_OK)

class DashboardView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Fetch quizzes first
        quizzes = Quiz.objects.all()
        quiz_data = []

        for quiz in quizzes:
            # Calculate total questions and update the quiz
            total_questions = quiz.calculate_total_questions()
            quiz.total_questions = total_questions  # Set the total_questions field
            quiz.save()  # Save the quiz with updated total_questions

            # Get categories for this quiz
            categories = Category.objects.filter(quiz=quiz)
            task_category = []

            for category in categories:
                # Get items within this category
                items = Item.objects.filter(category=category)
                task_items = []

                for item in items:
                    # Get quiz attempt data for the authenticated user (if any)
                    quiz_attempt_data = None
                    if request.user.is_authenticated:  # Assuming user is authenticated
                        quiz_attempt = QuizAttempt.objects.filter(user=request.user, item=item).first()
                        if quiz_attempt:
                            quiz_attempt_data = {
                                "total_questions": quiz_attempt.total_questions,
                                "correct_answers": quiz_attempt.correct_answers,
                                "wrong_answers": quiz_attempt.wrong_answers,
                                "score": quiz_attempt.score,
                            }

                    # Get leaderboard data for this item (Top 10 scorers)
                    leaderboard_data = Leaderboard.objects.filter(item=item).order_by('-score')[:10]
                    leaderboard = [
                        {
                            "user": entry.user.username,
                            "score": entry.score,
                            "rank": entry.rank,
                        }
                        for entry in leaderboard_data
                    ]

                    task_items.append({
                        "item_id": str(item.id),
                        "item_title": item.title,
                        "item_subtitle": item.subtitle,
                        "item_button_label": item.button_label or "Play",
                        "access_mode": item.access_mode or "public",
                        "item_type": item.item_type or "default",
                        "quiz_attempt": quiz_attempt_data,  # Include quiz attempt data if available
                        "leaderboard": leaderboard,  # Include leaderboard data
                    })

                task_category.append({
                    "category_id": str(category.id),
                    "category_title": category.title,
                    "category_type": category.category_type or "default",
                    "task_items": task_items,
                })

            quiz_data.append({
                "quiz_id": str(quiz.id),
                "quiz_title": quiz.title,
                "quiz_description": quiz.description,
                "total_questions": quiz.total_questions,  # Display the total number of questions
                "created_at": quiz.created_at,
                "updated_at": quiz.updated_at,
                "categories": task_category,
            })

        # Construct response
        return Response(
            {
                "response_type": "success",
                "is_logged_in": True if request.user.is_authenticated else False,
                "quiz_data": quiz_data,
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
        
        
        
class SubmitAnswerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        item_id = request.data.get("item_id")
        question_id = request.data.get("question_id")
        selected_option_id = request.data.get("selected_option_id")
        start_fresh = request.data.get("start_fresh", False)  # Flag for creating a new attempt on refresh
        next_question_index = request.data.get("current_question_index", 0) + 1

        try:
            question = Question.objects.get(id=question_id)
            selected_option = Option.objects.get(id=selected_option_id, question=question)
            item = Item.objects.get(id=item_id)
            category = item.category
            quiz = category.quiz  # Access the related Quiz
        except (Question.DoesNotExist, Option.DoesNotExist, Item.DoesNotExist, Category.DoesNotExist, Quiz.DoesNotExist):
            return Response(
                {"response_type": "error", "message": "Invalid question, option, or item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Negative marking value from the Quiz model
        negative_marking = quiz.negative_marking

        # Always create a new attempt if `start_fresh` is True
        if start_fresh:
            quiz_attempt = QuizAttempt.objects.create(
                user=request.user,
                item=item,
                total_questions=item.questions.count(),
                correct_answers=0,
                wrong_answers=0,
                score=0,
            )
        else:
            # Resume incomplete attempt or create a new one
            quiz_attempt = QuizAttempt.objects.filter(user=request.user, item=item).order_by('-attempt_date').first()
            if not quiz_attempt or (quiz_attempt.correct_answers + quiz_attempt.wrong_answers == quiz_attempt.total_questions):
                # No attempts or the last attempt is complete, create a new attempt
                quiz_attempt = QuizAttempt.objects.create(
                    user=request.user,
                    item=item,
                    total_questions=item.questions.count(),
                    correct_answers=0,
                    wrong_answers=0,
                    score=0,
                )

        # Check if the selected option is correct
        if selected_option.is_correct:
            quiz_attempt.correct_answers += 1
            quiz_attempt.score += 1  # Increment score for correct answer
        else:
            quiz_attempt.wrong_answers += 1
            quiz_attempt.score -= negative_marking  # Decrease score for wrong answer

        quiz_attempt.save()
        print(next_question_index)
        # Fetch next question
        questions = Question.objects.filter(item=item).order_by('id')
        if next_question_index < len(questions):
            next_question = questions[next_question_index]
            options = Option.objects.filter(question=next_question)
            answer_set = [
                {"answer_id": str(option.id), "answer": option.option_text}
                for option in options
            ]

            return Response(
                {
                    "response_type": "success",
                    "message": "Answer submitted successfully.",
                    "is_correct": selected_option.is_correct,
                    "next_question": {
                        "question_id": str(next_question.id),
                        "question": next_question.question_text,
                        "answer_set": answer_set,
                    },
                    "is_last_question": next_question_index + 1 >= len(questions),
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "response_type": "success",
                    "message": "Quiz completed successfully.",
                    "is_correct": selected_option.is_correct,
                    "score": quiz_attempt.score,
                    "correct_answers": quiz_attempt.correct_answers,
                    "wrong_answers": quiz_attempt.wrong_answers,
                },
                status=status.HTTP_200_OK
            )
