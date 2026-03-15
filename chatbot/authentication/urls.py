from django.urls import path
from authentication import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
  path('get_csrf/', views.setCSRFCookie.as_view()), #TODO: Ocultar
  path('users/', views.PostUser.as_view(), name='post-user'),
  path('login/', views.Login.as_view(), name='login'),
  path('logout/', views.Logout.as_view(), name='logout'),
  path('whoami/', views.RetrieveUser.as_view(), name='whoami'),
]