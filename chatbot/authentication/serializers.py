from rest_framework import serializers
from .models import User
from django.utils.translation import gettext_lazy as _
from django.core import validators

class LoginSerializer(serializers.ModelSerializer):
  email = serializers.CharField(validators=[validators.EmailValidator()])

  class Meta:
    model = User
    fields = ["email", "password"]

class UsersSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["id", "username", "email", "password"]
    extra_kwargs = {
        'id': {
          'read_only': True
        },
        'email': {
            'error_messages': {
                'blank': 'El correo esta en blanco',
                'required': 'El campo correo es requerido',
            }
        },
        'password': {
            'write_only': True,
            'error_messages': {
                'blank': 'La contraseña esta en blanco',
                'required': 'El campo contraseña es requerido',
            }
        },
        'username': {
            'error_messages': {
                'blank': 'El nombre de usuario esta en blanco',
                'required': 'El campo nombre de usuario es requerido',
            }
        },
    }
