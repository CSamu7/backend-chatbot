from rest_framework.permissions import BasePermission
from .models import Chat
from django.shortcuts import get_object_or_404

class MessagePermisions(BasePermission): 
  def has_permission(self, request, view):
    id_chat = view.kwargs["pk"]
    get_object_or_404(Chat, id=id_chat)

    return True
      