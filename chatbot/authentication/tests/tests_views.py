from rest_framework.test import APIRequestFactory, APIClient, force_authenticate
from rest_framework import status

from django.test import TestCase
from ..models import User
from ..views import RetrieveDeleteUser
import json

class AuthViewTestCase(TestCase):
  request_factory = APIRequestFactory()
  api_client = APIClient()
  raw_data_user = json.dumps({
    "email": "inventado@gmail.com",
    "password": "123"                                                                      
  })
    
  def setUp(self):
    User.objects.create_user(username="samu", password="123", email="inventado@gmail.com")

  def test_return_token_if_db_user_exists(self):
    response = self.client.post('/api/users/auth', data=self.raw_data_user, content_type="application/json")
    self.assertIs(response.status_code, status.HTTP_200_OK)

  def test_create_new_user(self):
    data = json.dumps({
      "username": "soynuevo",
      "email": "soynuevo@gmail.com",
      "password": "1234"
    })

    response = self.client.post('/api/users/', data=data, content_type="application/json")
    self.assertIs(response.status_code, status.HTTP_201_CREATED)

    user_created = User.objects.get(email="soynuevo@gmail.com")
    self.assertIsNotNone(user_created)

  def test_get_details_user_if_user_is_authenticated(self):
    user = User.objects.get(email="inventado@gmail.com")
    request = self.request_factory.get(f"/api/users/{user.pk}")
    force_authenticate(request, user=user)
    view = RetrieveDeleteUser().as_view()

    response = view(request, pk=user.pk)
    self.assertIs(response.status_code, status.HTTP_200_OK)
  
