from django.urls import path
from .views import DashboardView, GetQuestionsView, QuestionUploadView, CategoryCreateAPIView, ItemCreateAPIView

urlpatterns = [
    path('category/create/', CategoryCreateAPIView.as_view(), name='create-category'),
    path('item/create/', ItemCreateAPIView.as_view(), name='create-item'),
    path('upload-questions/', QuestionUploadView.as_view(), name='upload-questions'), 
    path('get-questions/', GetQuestionsView.as_view(), name='get-questions'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
