from django.urls import path
from authentication import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
  path('users/<int:pk>', views.RetrieveDeleteUser.as_view()),
  path('users/', views.PostUser.as_view()),
  path('users/auth', views.Login.as_view()),
]