from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
  username = models.CharField(max_length=50)
  email = models.EmailField(validators=[validators.EmailValidator()], unique=True)
  is_superuser = models.BooleanField(default=False)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username"]

  objects = CustomUserManager()

  def __str__(self):
    return self.username

  def has_perm(self, perm, obj=None):
    return True
  
  def has_module_perms(self, app_label):
    return True

  def is_staff(self):
    return self.is_admin
  
