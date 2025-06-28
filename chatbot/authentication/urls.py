from django.urls import path
from authentication import views

urlpatterns = [
  # path('auth/', views.UserAuth.as_view()),
  path('user/', views.UserPost.as_view()),
  path('user/<int:pk>', views.UserDetails.as_view())
]