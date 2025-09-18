from authentication.serializers import UsersSerializer
from authentication.models import User
from rest_framework import generics, status
from .permissions import UserPermissions
from rest_framework.authtoken.views import ObtainAuthToken 
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import CustomAuthSerializer
from rest_framework.views import APIView

class PostUser(APIView):
  authentication_classes = []
  permission_classes = []

  def post(self, request, *args, **kwargs):
    serializer = UsersSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()

      user = User.objects.get(email=serializer.data["email"])
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

class CustomAuthToken(ObtainAuthToken):
  serializer_class = CustomAuthSerializer

  def post(self, request, *args, **kwargs):
      serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
      serializer.is_valid(raise_exception=True)
      user = serializer.validated_data['user']
      token, created = Token.objects.get_or_create(user=user)
      
      return Response({
            'token': token.key,
            'user_id': user.pk,
      })