from authentication.serializers import UsersSerializer
from authentication.models import User
from rest_framework import generics

class PostUser(generics.CreateAPIView):
  serializer_class = UsersSerializer

class RetrieveDeleteUser(generics.RetrieveDestroyAPIView):
  queryset = User.objects.all()
  serializer_class = UsersSerializer
