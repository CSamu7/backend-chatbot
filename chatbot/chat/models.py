from django.db import models
from authentication.models import User

class Chat(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=150)
  last_genre = models.CharField(max_length=100, null=True, blank=True)
  seen_books = models.JSONField(default=list)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title
  
  class Meta:
    ordering = ["created_at"]

class Message(models.Model):
  its_from_user = models.BooleanField(default=False)
  chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
  text = models.TextField()
  libro_ids = models.JSONField(default=list, blank=True)
  send_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering = ["send_at"]

  def __str__(self):
    return self.text[:50] if len(self.text) > 50 else self.text

def historial(user: User, text: str, chat: Chat):
    Message.objects.create(
        user=user,
        chat=chat,
        text=text,
        send_at=None  
    )
    