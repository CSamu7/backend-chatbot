from authentication.serializers import UsersSerializer
from authentication.models import User
from rest_framework import generics, status
from .permissions import UserPermissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
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
    
    token, created = Token.objects.get_or_create(user=user)

    response = Response({"id_user": user.id, "token": token.key })
    return response

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

class RetrieveDeleteUser(generics.RetrieveDestroyAPIView):
  queryset = User.objects.all()
  serializer_class = UsersSerializer
  permission_classes = [UserPermissions]
  authentication_classes = [TokenAuthentication]