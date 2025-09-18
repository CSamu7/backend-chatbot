from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import bad_request, AuthenticationFailed, NotFound

class UsersSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["username", "email", "password"]
    extra_kwargs = {
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

class CustomAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            msg = _('Debes incluir tu correo o contraseña".')
            raise serializers.ValidationError(msg)

        user = authenticate(email=email, password=password) 

        if user:
            if not user.is_active:
                msg = _('Tu cuenta esta desactivada.')
                raise AuthenticationFailed(msg)
        else:
            msg = _('Correo/contraseña incorrectos')
            raise NotFound(msg)

        attrs['user'] = user
        return attrs