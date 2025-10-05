from authentication.serializers import UsersSerializer
from authentication.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_protect

ensure_csrf = method_decorator(ensure_csrf_cookie)
class setCSRFCookie(APIView):
    permission_classes = []
    authentication_classes = []
    @ensure_csrf
    def get(self, request):
        return Response("CSRF Cookie set.")

class Logout(APIView):
  def get(self, request, *args, **kwargs):
    logout(request=request)
    return Response(status=status.HTTP_205_RESET_CONTENT)

csrf_protect_method = method_decorator(csrf_protect)
class Login(APIView):
  authentication_classes = []
  permission_classes = [AllowAny]

  def post(self, request, *args, **kwargs):
    user = authenticate(request, email=request.data["email"], password=request.data["password"])

    if not user:
      return Response({"error": "Correo/contraseña incorrecto"}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
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
