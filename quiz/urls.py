from django.urls import path
from .views import DashboardView, GetQuestionsView, QuestionUploadView

urlpatterns = [
    path('upload-questions/', QuestionUploadView.as_view(), name='upload-questions'), 
    path('get-questions/', GetQuestionsView.as_view(), name='get-questions'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
