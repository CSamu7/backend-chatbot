from rest_framework.permissions import BasePermission

class ChatPermissions(BasePermission):
  def has_permission(self, request, view):
    return request.user.id == view.kwargs["pk"]

  def has_object_permission(self, request, view, obj):
    return request.user == obj.user