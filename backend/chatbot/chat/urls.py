from django.urls import path
from chat import views

urlpatterns = [
  path('users/<int:pk>/chats/', views.ListChats.as_view()),
  path('chats/', views.PostChat.as_view()),
  path('chats/<int:pk>', views.RetrieveModifyDeleteChat.as_view()),
  path('chats/<int:pk>/messages/', views.ListPostMessage.as_view()),
]