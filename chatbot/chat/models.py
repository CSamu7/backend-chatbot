from django.db import models
from authentication.models import User

# Create your models here.
class Chat(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=150)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

class Message(models.Model):
  chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  text = models.TextField()
  send_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.text[:50] if len(self.text) > 50 else self.text
