from rest_framework import serializers
from .models import User

class UsersSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["username", "email", "is_active"]
    extra_kwargs = {'password': {'write_only': True}}

  