from authentication.serializers import UsersSerializer
from authentication.models import User
from rest_framework import generics, status
from .permissions import UserPermissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
import pprint

class Login(APIView):
  authentication_classes = []
  permission_classes = []

  def post(self, request, *args, **kwargs):
    user = get_object_or_404(User, email=request.data["email"])

    if not user.check_password(request.data["password"]):
      return Response({"error": "Correo/contraseña incorrecto"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UsersSerializer(user)
    return Response(serializer.data)

class PostUser(APIView):
  def post(self, request, *args, **kwargs):
    serializer = UsersSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()

      user = User.objects.get(email=serializer.data["email"])
      user.set_password(serializer.data["password"])
      user.save()

      token = Token.objects.create(user=user)

      return Response({
        'user_id': user.id,
        'token': token.key
      }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveUser(APIView):
  queryset = User.objects.all()
  serializer_class = UsersSerializer

  def get(self, request, format=None):
    if not request.user.is_authenticated:
        return Response({'isAuthenticated': False})

    return Response({'id': request.user.id, 'username': request.user.username, 'email': request.user.email})
