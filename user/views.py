from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, get_user_model

from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User registered successfully"
            },
            status=status.HTTP_201_CREATED,
        )

class UserLoginView(generics.GenericAPIView):
    """
    API view for user login.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get data from request
        serializer = self.get_serializer(data=request.data)
        
        # Validate the serializer
        serializer.is_valid(raise_exception=True)

        # Return tokens
        return Response(
            {
                "access_token": serializer.validated_data['access_token'],
                "refresh_token": serializer.validated_data['refresh_token'],
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Allow admins to view all users; regular users only see their own data.
        """
        if self.request.user.is_staff:
            return super().get_queryset()
        return User.objects.filter(id=self.request.user.id)
