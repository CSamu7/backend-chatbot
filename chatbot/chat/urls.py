from django.urls import path
from chat import views
from chat import api_views

urlpatterns = [
  path('users/<int:pk>/chats/', views.ListPostChats.as_view()),
  path('chats/<int:pk>', views.RetrieveDeleteChat.as_view()),
  path('chats/<int:pk>/messages/', views.ListPostMessage.as_view()),
  path('chats/<int:chat_id>/history/', api_views.get_chat_history, name='chat-history'),
  path('chats/<str:email>/', api_views.get_user_chats, name='chat-user-chats'),
  path('chatbot/ask/', views.ChatbotAPIView.as_view()),
  path('chatbot/', api_views.chatbot_api, name='chatbot-api'),
  path('chatbot/info/', api_views.chatbot_info, name='chatbot-info'),
]