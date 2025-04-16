from django.urls import path
from .views import *

urlpatterns = [
    path('quiz/create/', QuizCreateAPIView.as_view(), name='create-quiz'),
    path('category/create/', CategoryCreateAPIView.as_view(), name='create-category'),
    path('item/create/', ItemCreateAPIView.as_view(), name='create-item'),
    path("category/update/<int:pk>/", CategoryPartialUpdateAPIView.as_view(), name="category-update"),
    path("item/update/<int:pk>/", ItemPartialUpdateAPIView.as_view(), name="item-update"),
    path('upload-questions/', QuestionUploadView.as_view(), name='upload-questions'), 
    path('get-questions/', GetQuestionsView.as_view(), name='get-questions'),
    path('submit-answer/', SubmitAnswersView.as_view(), name='submit_answer'),
    # path('quiz/question/', GetQuestionView.as_view(), name='get_question'),  # For the first question
    # path('quiz/question/<int:question_id>/', GetQuestionView.as_view(), name='get_next_question'),
    # path('get-question/<int:question_id>/', GetQuestionView.as_view(), name='get-question'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
