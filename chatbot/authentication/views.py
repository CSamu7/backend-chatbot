from authentication.models import User
from authentication.serializers import UsersSerializer

from rest_framework.views import APIView
from rest_framework import mixins, generics, status
from rest_framework.response import Response

from rest_framework.authtoken.models import Token

# class UserAuth(APIView):
#   serializer_class = UsersSerializer

#   def auth(self, request):
#     email = request.data.email
#     password = request.data.password

#     try:
#       user = User.objects.get(email=email, password=password)
#       token = Token.objects.create(user)

#       return Response(token)
#     except:
#       return Response(status=status.HTTP_401_UNAUTHORIZED)

#Generico
class UserPost(generics.GenericAPIView, mixins.CreateModelMixin):
  serializer_class = UsersSerializer

  def create(self, request, *args, **kwargs):
    return self.list(request, *args, **kwargs)
  
class UserDetails(generics.RetrieveUpdateDestroyAPIView):
  queryset = User.objects.all()
  serializer_class = UsersSerializer
