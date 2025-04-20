from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.permissions import AllowAny
import pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from .models import *
from .serializers import *
from user.models import *
import uuid



class QuizCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            quiz = serializer.save()
            quiz.calculate_total_questions()  # Calculate total questions after saving
            return Response(
                {
                    "type": "success",
                    "message": "Quiz created successfully",
                    "data": {
                        "quiz": serializer.data,
                    }
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "type": "error",
                "message": "Invalid data provided",
                "data": {
                    "quiz": serializer.errors,
                }
            },
            status=status.HTTP_200_OK,
        )

        
        
        
class CategoryCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize the data
        serializer = CategorySerializer(data=request.data)
        
        # Check if the data is valid
        if serializer.is_valid():
            category = serializer.save()  # Save the category
            return Response({
                "type": "success",
                "message": "Category created successfully",
                "data": {
                    "category": serializer.data,
                }
            }, status.HTTP_200_OK)
        
        # If invalid, return errors with the same response format
        return Response({
            "type": "error",
            "message": "Category creation failed.",
            "data": {
                "category": serializer.errors,
            }
        }, status=status.HTTP_200_OK)



class CategoryPartialUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({
                "type": "error",
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "type": "success",
                "message": "Category updated successfully",
                "data": {
                    "data": serializer.data,
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "type": "error",
            "message": "Category update failed.",
            "data": {
                "category": serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class ItemCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize the data for Item creation
        serializer = ItemSerializer(data=request.data)
        
        # Check if the data is valid
        if serializer.is_valid():
            item = serializer.save()  # Save the item
            return Response(
                {
                    "type": "success",
                    "message": "Item created successfully",
                    "data": {
                        "item": serializer.data,
                    }
                },
                status=status.HTTP_200_OK
            )
        
        # If invalid, return errors with the same structure
        return Response(
            {
                "type": "error",
                "message": "Invalid data provided",
                "data": {
                    "item": serializer.errors,
                }
            },
            status=status.HTTP_200_OK
        )


class ItemPartialUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({
                "type": "error",
                "message": "Item not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "type": "success",
                "message": "Item updated successfully",
                "data": {
                    "item": serializer.data,
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "type": "error",
            "message": "Item update failed.",
            "data": {
                "item": serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    
class GetQuestionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = []  # Optional if you want to handle auth manually

    def post(self, request, *args, **kwargs):
        category_id = request.data.get('category_id')
        item_id = request.data.get('item_id')
        current_question_index = int(request.data.get('current_question_index', 0))

        try:
            category = Category.objects.get(id=category_id)
            item = Item.objects.get(id=item_id, category=category)
        except Category.DoesNotExist:
            return Response(
                {
                    "type": "error",
                    "message": "Category not found.",
                    "data": {"questions": "Category not found."}
                },
                status=status.HTTP_200_OK
            )
        except Item.DoesNotExist:
            return Response(
                {
                    "type": "error",
                    "message": "Item not found in the specified category.",
                    "data": {"questions": "Item not found."}
                },
                status=status.HTTP_200_OK
            )

        # Access control
        if item.access_mode == "private" and not request.user.is_authenticated:
            return Response(
                {
                    "type": "error",
                    "message": "Authentication required to access this item.",
                    "data": {"questions": "Unauthorized access."}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        questions = item.questions.all()

        if not questions.exists():
            return Response(
                {
                    "type": "error",
                    "message": "No questions linked to this item.",
                    "data": {"questions": "No questions found."}
                },
                status=status.HTTP_200_OK
            )

        if current_question_index < 0 or current_question_index >= questions.count():
            return Response(
                {
                    "type": "error",
                    "message": "Invalid question index.",
                    "data": {"questions": "Invalid question index."}
                },
                status=status.HTTP_200_OK
            )

        question = questions[current_question_index]
        options = Option.objects.filter(question=question)

        answer_set = [
            {
                "answer_id": str(option.id),
                "answer": option.option_text,
                "is_true": option.is_correct
            }
            for option in options
        ]

        return Response(
            {
                "type": "success",
                "message": "Question fetched successfully",
                "data": {
                    "questions": [
                        {
                            "question_id": str(question.id),
                            "question": question.question_text,
                            "answer_set": answer_set
                        }
                    ],
                    "next_question_index": current_question_index + 1 if current_question_index + 1 < questions.count() else None,
                    "is_last_question": current_question_index + 1 >= questions.count()
                }
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

# class DashboardView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Initialize response data
#         user = None
#         is_logged_in = False
#         response_type = "success"
#         message = "Dashboard fetched successfully"
#         status_code = status.HTTP_200_OK

#         # Attempt JWT authentication
#         try:
#             jwt_auth = JWTAuthentication()
#             auth_result = jwt_auth.authenticate(request)  # Returns (user, auth) or None

#             if auth_result is not None:
#                 user, auth = auth_result
#                 is_logged_in = True
#         except (InvalidToken, AuthenticationFailed):
#             response_type = "error"
#             message = "Invalid or expired token"
#             status_code = status.HTTP_200_OK  # Unauthorized response

#         # Fetch quizzes
#         quizzes = Quiz.objects.all()
#         quiz_data = []

#         for quiz in quizzes:
#             total_questions = quiz.calculate_total_questions()
#             quiz.total_questions = total_questions
#             quiz.save()

#             categories = Category.objects.filter(quiz=quiz)
#             task_category = []

#             for category in categories:
#                 items = Item.objects.filter(category=category)
#                 task_items = []

#                 for item in items:
#                     quiz_attempt_data = None
#                     if user:  # Include user-specific quiz attempt data only if authenticated
#                         quiz_attempt = QuizAttempt.objects.filter(user=user, item=item).first()
#                         if quiz_attempt:
#                             quiz_attempt_data = {
#                                 "total_questions": quiz_attempt.total_questions,
#                                 "correct_answers": quiz_attempt.correct_answers,
#                                 "wrong_answers": quiz_attempt.wrong_answers,
#                                 "score": quiz_attempt.score,
#                             }

#                     leaderboard_data = Leaderboard.objects.filter(item=item).order_by('-score')[:10]
#                     leaderboard = [
#                         {
#                             "user": entry.user.username,
#                             "score": entry.score,
#                             "rank": entry.rank,
#                         }
#                         for entry in leaderboard_data
#                     ]

#                     task_items.append({
#                         "item_id": str(item.id),
#                         "item_title": item.title,
#                         "item_subtitle": item.subtitle,
#                         "item_button_label": item.button_label or "Play",
#                         "access_mode": item.access_mode or "public",
#                         "item_type": item.item_type or "default",
#                         "quiz_attempt": quiz_attempt_data,  # Only if user is authenticated
#                         "leaderboard": leaderboard,  # Always included
#                     })

#                 task_category.append({
#                     "category_id": str(category.id),
#                     "category_title": category.title,
#                     "category_type": category.category_type or "default",
#                     "task_items": task_items,
#                 })

#             quiz_data.append({
#                 "quiz_id": str(quiz.id),
#                 "quiz_title": quiz.title,
#                 "quiz_description": quiz.description,
#                 "total_questions": quiz.total_questions,
#                 "created_at": quiz.created_at,
#                 "updated_at": quiz.updated_at,
#                 "categories": task_category,
#             })

#         # Construct response
#         return Response(
#             {
#                 "type": response_type,  # "success" or "error"
#                 "message": message,
#                 "data": {
#                     "is_logged_in": is_logged_in,
#                     "data": quiz_data,  # Renamed to "quizzes" for clarity
#                 },
#             },
#             status=status.HTTP_200_OK
#         )
        
        
class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]  # Allow access, but restrict private content

    def get(self, request, *args, **kwargs):
        user = None
        response_type = "success"
        message = "Dashboard fetched successfully"

        # Authenticate the user using JWT
        try:
            jwt_auth = JWTAuthentication()
            auth_result = jwt_auth.authenticate(request)  # Returns (user, auth) or None
            if auth_result:
                user, auth = auth_result  # Set user if authentication is successful
        except AuthenticationFailed:
            pass  # User remains None if authentication fails

        # Get the user_transaction_id (from session or user)
        if user:
            # If the user is authenticated, set a guest-like identifier or exclude the ID
            user_transaction_id = None  # Do not send user.id for authenticated users
        else:
            # If the user is not authenticated, get the guest ID from session
            user_transaction_id = request.session.get("guest_id")

        quizzes = Quiz.objects.all()
        quiz_data = []

        for quiz in quizzes:
            categories = Category.objects.filter(quiz=quiz)
            filtered_categories = []

            for category in categories:
                # Hide private categories for unauthenticated users
                if not user and category.access_mode == "private":
                    continue  

                items = Item.objects.filter(category=category)
                filtered_items = []

                for item in items:
                    # Hide private items for unauthenticated users
                    if not user and item.access_mode == "private":
                        continue  

                    quiz_attempt_data = None
                    if user:
                        quiz_attempt = QuizAttempt.objects.filter(user=user, item=item).first()
                        if quiz_attempt:
                            quiz_attempt_data = {
                                "total_questions": quiz_attempt.total_questions,
                                "correct_answers": quiz_attempt.correct_answers,
                                "wrong_answers": quiz_attempt.wrong_answers,
                                "score": quiz_attempt.score,
                            }

                    leaderboard_data = Leaderboard.objects.filter(item=item).order_by('-score')[:10]
                    leaderboard = [
                        {
                            "user": entry.user.username,
                            "score": entry.score,
                            "rank": entry.rank,
                        }
                        for entry in leaderboard_data
                    ]

                    filtered_items.append({
                        "item_id": str(item.id),
                        "item_title": item.title,
                        "item_subtitle": item.subtitle,
                        "item_button_label": item.button_label or "Play",
                        "access_mode": item.access_mode or "public",
                        "item_type": item.item_type or "default",
                        "quiz_attempt": quiz_attempt_data,
                        "leaderboard": leaderboard,
                    })

                # Ensure authenticated users see private categories
                if user or filtered_items:
                    filtered_categories.append({
                        "category_id": str(category.id),
                        "category_title": category.title,
                        "category_type": category.category_type or "default",
                        "access_mode": category.access_mode,
                        "task_items": filtered_items,
                    })

            quiz_data.append({
                "quiz_id": str(quiz.id),
                "quiz_title": quiz.title,
                "quiz_description": quiz.description,
                "total_questions": quiz.total_questions,
                "created_at": quiz.created_at,
                "updated_at": quiz.updated_at,
                "categories": filtered_categories,
            })

        return Response(
            {
                "type": response_type,
                "message": message,
                "data": {
                    "quizzes": quiz_data,
                    "access_token": user_transaction_id  # Send None or guest ID here
                },
                
            },
            status=status.HTTP_200_OK
        )


        
# class QuestionUploadView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         # Ensure a file is provided
#         file = request.FILES.get('file')
#         if not file:
#             return Response(
#                 {
#                     "type": "error",
#                     "message": "No file uploaded.",
#                     "data": {},
#                 },
#                 status=status.HTTP_200_OK
#             )

#         try:
#             # Parse the uploaded Excel file
#             df = pd.read_excel(file)

#             # Expected columns
#             required_columns = [
#                 'Question', 'Subject', 'Category', 'Options_num', 
#                 'Option1', 'Option2', 'Option3', 'Option4', 'Answer'
#             ]

#             if not all(col in df.columns for col in required_columns):
#                 return Response(
#                     {
#                         "type": "error",
#                         "message": "Excel file is missing required columns.",
#                         "data": {},
#                     },
#                     status=status.HTTP_200_OK
#                 )

#             with transaction.atomic():  # Ensure atomicity
#                 for _, row in df.iterrows():
#                     # Retrieve or validate category and subject (assuming Item represents Subject here)
#                     category_id = row['Category']
#                     subject_id = row['Subject']
#                     question_text = row['Question']
#                     options_num = int(row['Options_num'])
#                     answers = row['Answer'].split(',')  # Expected format: "Option1,Option3"
#                     answers = [answer.strip().capitalize() for answer in answers]  # Ensure answers are properly formatted

#                     # Fetch or create category and subject
#                     category, created = Category.objects.get_or_create(id=category_id)
#                     item, created = Item.objects.get_or_create(id=subject_id)

#                     # Create or update the question
#                     question, created = Question.objects.get_or_create(
#                         question_text=question_text,
#                         item=item
#                     )

#                     # Create or update options
#                     for i in range(1, options_num + 1):
#                         option_text = row.get(f'Option{i}')
#                         if option_text:
#                             option_text = option_text.capitalize()  # Convert option text to match format (e.g., Option1)
#                             is_correct = f'Option{i}'.capitalize() in answers
#                             Option.objects.update_or_create(
#                                 question=question,
#                                 option_text=option_text,
#                                 defaults={'is_correct': is_correct}
#                             )

#             return Response(
#                 {
#                     "type": "success",
#                     "message": "Questions uploaded successfully!",
#                     "data": {},
#                 },
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {
#                     "type": "error",
#                     "message": str(e),
#                     "data": {},
#                 },
#                 status=status.HTTP_200_OK
#             )


class QuestionUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {
                    "type": "error",
                    "message": "No file uploaded.",
                    "data": {},
                },
                status=status.HTTP_200_OK
            )

        try:
            df = pd.read_excel(file)

            required_columns = [
                'Question', 'Subject', 'Category', 'Options_num',
                'Option1', 'Option2', 'Option3', 'Option4', 'Answer'
            ]

            if not all(col in df.columns for col in required_columns):
                return Response(
                    {
                        "type": "error",
                        "message": "Excel file is missing required columns.",
                        "data": {},
                    },
                    status=status.HTTP_200_OK
                )
            print("hello")

            with transaction.atomic():
                
                for _, row in df.iterrows():
                    
                    category_id = str(row.get('Category')).strip() if not pd.isna(row.get('Category')) else None
                    subject_id = str(row.get('Subject')).strip() if not pd.isna(row.get('Subject')) else None
                    question_text = str(row.get('Question')).strip() if not pd.isna(row.get('Question')) else None
                    options_num = int(row.get('Options_num')) if not pd.isna(row.get('Options_num')) else 0
                    answer_field = str(row.get('Answer')).strip() if not pd.isna(row.get('Answer')) else ""
                    answers = [a.strip().capitalize() for a in answer_field.split(',') if a.strip()]

                    # if not all([category_id, subject_id, question_text]) or options_num == 0:
                    #     continue  # Skip incomplete rows
                    
                    
                    # Check if the category exists
                    category = Category.objects.get(id=category_id)
                    
                    if not category:
                        return Response(
                            {
                                "type": "error",
                                "message": f"Category with ID {category_id} not found.",
                                "data": {},
                            },
                            status=status.HTTP_200_OK
                        )

                    # Check if the item exists
                    item = Item.objects.filter(id=subject_id, category=category).first()
                    if not item:
                        return Response(
                            {
                                "type": "error",
                                "message": f"Item with ID {subject_id} in Category {category.title} not found.",
                                "data": {},
                            },
                            status=status.HTTP_200_OK
                        )
                        
                    

                    # Create or get the question
                    question, _ = Question.objects.get_or_create(question_text=question_text)
                    
                    # Link question to item (many-to-many relationship)
                    item.questions.add(question)

                    # Add options for the question
                    options = []
                    i = 1
                    while True:
                        option_col = f'Option{i}'
                        option_text = row.get(option_col)
                        if pd.isna(option_text):  # Break the loop if no more options are found
                            break
                        options.append(option_text.strip().capitalize())
                        i += 1

                    # If there are options, create/update them
                    for option_text in options:
                        is_correct = option_text in answers  # Check if the option is correct
                        Option.objects.update_or_create(
                            question=question,
                            option_text=option_text,
                            defaults={'is_correct': is_correct}
                        )
            
            return Response(
                {
                    "type": "success",
                    "message": "Questions uploaded successfully!",
                    "data": {},
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "type": "error",
                    "message": str(e),
                    "data": {},
                },
                status=status.HTTP_200_OK
            )


        
        
# class SubmitAnswerView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         item_id = request.data.get("item_id")
#         question_id = request.data.get("question_id")
#         selected_option_id = request.data.get("selected_option_id")
#         start_fresh = request.data.get("start_fresh", False)  # Flag for creating a new attempt on refresh
#         next_question_index = request.data.get("current_question_index", 0) + 1

#         try:
#             question = Question.objects.get(id=question_id)
#             selected_option = Option.objects.get(id=selected_option_id, question=question)
#             item = Item.objects.get(id=item_id)
#             category = item.category
#             quiz = category.quiz  # Access the related Quiz
#         except (Question.DoesNotExist, Option.DoesNotExist, Item.DoesNotExist, Category.DoesNotExist, Quiz.DoesNotExist):
#             return Response(
#                 {
#                     "type": "error",
#                     "message": "Invalid question, option, or item.",
#                     "data": {},
#                 },
#                 status=status.HTTP_200_OK
#             )

#         # Negative marking value from the Quiz model
#         negative_marking = quiz.negative_marking

#         # Always create a new attempt if `start_fresh` is True
#         if start_fresh:
#             quiz_attempt = QuizAttempt.objects.create(
#                 user=request.user,
#                 item=item,
#                 total_questions=item.questions.count(),
#                 correct_answers=0,
#                 wrong_answers=0,
#                 score=0,
#             )
#         else:
#             # Resume incomplete attempt or create a new one
#             quiz_attempt = QuizAttempt.objects.filter(user=request.user, item=item).order_by('-attempt_date').first()
#             if not quiz_attempt or (quiz_attempt.correct_answers + quiz_attempt.wrong_answers == quiz_attempt.total_questions):
#                 # No attempts or the last attempt is complete, create a new attempt
#                 quiz_attempt = QuizAttempt.objects.create(
#                     user=request.user,
#                     item=item,
#                     total_questions=item.questions.count(),
#                     correct_answers=0,
#                     wrong_answers=0,
#                     score=0,
#                 )

#         # Check if the selected option is correct
#         if selected_option.is_correct:
#             quiz_attempt.correct_answers += 1
#             quiz_attempt.score += 1  # Increment score for correct answer
#         else:
#             quiz_attempt.wrong_answers += 1
#             quiz_attempt.score -= negative_marking  # Decrease score for wrong answer

#         quiz_attempt.save()

#         # Fetch next question
#         questions = Question.objects.filter(item=item).order_by('id')
#         if next_question_index < len(questions):
#             next_question = questions[next_question_index]
#             options = Option.objects.filter(question=next_question)
#             answer_set = [
#                 {"answer_id": str(option.id), "answer": option.option_text}
#                 for option in options
#             ]

#             return Response(
#                 {
#                     "type": "success",
#                     "message": "Answer submitted successfully.",
#                     "data":{
#                         "data": {
#                             "is_correct": selected_option.is_correct,
#                             "next_question": {
#                                 "question_id": str(next_question.id),
#                                 "question": next_question.question_text,
#                                 "answer_set": answer_set,
#                             },
#                             "is_last_question": next_question_index + 1 >= len(questions),
#                         },
#                     } 
#                 },
#                 status=status.HTTP_200_OK
#             )
#         else:
#             return Response(
#                 {
#                     "type": "success",
#                     "message": "Quiz completed successfully.",
#                     "data": {
#                         "is_correct": selected_option.is_correct,
#                         "score": quiz_attempt.score,
#                         "correct_answers": quiz_attempt.correct_answers,
#                         "wrong_answers": quiz_attempt.wrong_answers,
#                     },
#                 },
#                 status=status.HTTP_200_OK
#             )

class SubmitAnswersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        item_id = request.data.get("item_id")
        answers = request.data.get("answers", [])
        start_fresh = request.data.get("start_fresh", False)

        try:
            item = Item.objects.get(id=item_id)
            category = item.category
            quiz = category.quiz
        except (Item.DoesNotExist, Category.DoesNotExist, Quiz.DoesNotExist):
            return Response(
                {"type": "error", "message": "Invalid item or quiz.", "data": {}},
                status=status.HTTP_400_BAD_REQUEST
            )

        negative_marking = quiz.negative_marking

        # Create or resume QuizAttempt
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
            quiz_attempt = QuizAttempt.objects.filter(user=request.user, item=item).order_by('-attempt_date').first()
            if not quiz_attempt or (quiz_attempt.correct_answers + quiz_attempt.wrong_answers == quiz_attempt.total_questions):
                quiz_attempt = QuizAttempt.objects.create(
                    user=request.user,
                    item=item,
                    total_questions=item.questions.count(),
                    correct_answers=0,
                    wrong_answers=0,
                    score=0,
                )

        result_data = []

        for answer in answers:
            question_id = answer.get("question_id")
            selected_option_ids = answer.get("selected_option_ids", [])

            try:
                question = Question.objects.get(id=question_id, item=item)
            except Question.DoesNotExist:
                continue  # Skip invalid question

            correct_options = set(
                Option.objects.filter(question=question, is_correct=True).values_list("id", flat=True)
            )
            selected_set = set(selected_option_ids)

            is_correct = selected_set == correct_options

            if is_correct:
                quiz_attempt.correct_answers += 1
                quiz_attempt.score += 1
            else:
                quiz_attempt.wrong_answers += 1
                quiz_attempt.score -= negative_marking

            result_data.append({
                "question_id": question_id,
                "is_correct": is_correct,
                "selected_options": list(selected_set),
                "correct_options": list(correct_options),
            })

        quiz_attempt.save()

        return Response(
            {
                "type": "success",
                "message": "All answers submitted successfully.",
                "data": {
                    "results": result_data,
                    "score": quiz_attempt.score,
                    "correct_answers": quiz_attempt.correct_answers,
                    "wrong_answers": quiz_attempt.wrong_answers,
                    "total_questions": quiz_attempt.total_questions,
                    "quiz_completed": (
                        quiz_attempt.correct_answers + quiz_attempt.wrong_answers == quiz_attempt.total_questions
                    ),
                },
            },
            status=status.HTTP_200_OK
        )
