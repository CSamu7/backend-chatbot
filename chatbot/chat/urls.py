from django.urls import path
from chat import views
from chat import api_views

urlpatterns = [
  path('users/<int:pk>/chats/', views.ListChats.as_view(), name='chat-list'),
  path('chats/', views.PostChat.as_view(), name='chat-post'),
  path('chats/<int:pk>', views.RetrieveModifyDeleteChat.as_view(), name='chat-detail'),
  path('chats/<int:pk>/messages/', views.ListMessage.as_view(), name='message-list'),
  path('chats/<int:pk>/messages/', views.PostMessage.as_view()),
  path('chatbot/ask/', views.ChatbotAPIView.as_view()),
  path('chatbot/', api_views.chatbot_api, name='chatbot-api'),
]