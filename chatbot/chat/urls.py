from django.urls import path
from chat import views

urlpatterns = [
  path('users/<int:pk>/chats/', views.ListPostChats.as_view()),
  path('chats/<int:pk>', views.RetrieveDeleteChat.as_view()),
  path('chats/<int:pk>/messages/', views.ListPostMessage.as_view()),
]