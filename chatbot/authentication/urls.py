from django.urls import path
from authentication import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
  path('get_csrf/', views.setCSRFCookie.as_view()),
  path('users/', views.PostUser.as_view()),
  path('login/', views.Login.as_view()),
  path('logout/', views.Logout.as_view()),
  path('whoami/', views.RetrieveUser.as_view()),
]