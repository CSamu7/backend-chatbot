from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
  username = models.CharField(max_length=50)
  email = models.EmailField(validators=[validators.EmailValidator()], unique=True)

  def __str__(self):
    return self.username

class Chat(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=150)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name

class Message(models.Model):
  chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
  content = models.TextField()
  send_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.content[:50] if self.content > 50 else self.content

