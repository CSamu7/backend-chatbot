from django.urls import path
from authentication import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
  path('users/<int:pk>', views.RetrieveDeleteUser.as_view()),
  path('users/', views.PostUser.as_view()),
  path('users/auth', TokenObtainPairView.as_view(), name="token_obtain"),
  path('users/auth/refresh', TokenRefreshView.as_view(), name="token_refresh")
]