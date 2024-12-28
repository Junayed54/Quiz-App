from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserRegistrationView, UserLoginView, UserViewSet

# Create a router for the UserViewSet
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    # User registration endpoint
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # User login endpoint
    path('login/', UserLoginView.as_view(), name='user-login'),
    # Include the router URLs for the UserViewSet
    path('', include(router.urls)),
]
