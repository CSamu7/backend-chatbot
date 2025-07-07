from django.urls import path
from authentication import views

urlpatterns = [
  path('users/<int:pk>', views.RetrieveDeleteUser.as_view()),
  path('users/', views.PostUser.as_view())
]