from authentication.serializers import UsersSerializer
from authentication.models import User
from rest_framework import generics, permissions
from .permissions import UserPermissions
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenView(TokenObtainPairView):
  permission_classes = []

class PostUser(generics.CreateAPIView):
  serializer_class = UsersSerializer
  authentication_classes = []
  permission_classes = []

class RetrieveDeleteUser(generics.RetrieveDestroyAPIView):
  queryset = User.objects.all()
  serializer_class = UsersSerializer
  permission_classes = [UserPermissions]
