from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
  username = models.CharField(max_length=50)
  email = models.EmailField(validators=[validators.EmailValidator()], unique=True)

  USERNAME_FIELD = "email"
  EMAIL_FIELD = "email"

  def __str__(self):
    return self.username
