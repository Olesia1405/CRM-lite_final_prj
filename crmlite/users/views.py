from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer, UserRegisterSerializer
from .models import User

@extend_schema(
    tags=['Authentication'],
    description='Регистрация нового пользователя',
    responses={
        201: UserSerializer,
        400: None,
    }
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
