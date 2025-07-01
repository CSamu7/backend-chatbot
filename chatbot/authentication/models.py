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

class Chat(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=150)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

class Message(models.Model):
  chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  content = models.TextField()
  send_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.content[:50] if len(self.content) > 50 else self.content
