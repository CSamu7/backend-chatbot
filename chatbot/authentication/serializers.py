from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import bad_request, AuthenticationFailed, NotFound

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
                'required': 'El campo correo no se encuentra',
            }
        },
        'password': {
            'write_only': True,
            'error_messages': {
                'blank': 'La contraseña esta en blanco',
                'required': 'El campo contraseña no se encuentra',
            }
        },
        'username': {
            'error_messages': {
                'blank': 'El nombre de usuario esta en blanco',
                'required': 'El campo nombre de usuario no se encuentra',
            }
        },
    }
