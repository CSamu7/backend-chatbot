from rest_framework.test import APIRequestFactory
from django.test import TestCase
from ..models import User

# Create your tests here.
class AuthViewTestCase(TestCase):
  factory = APIRequestFactory()
    
  def setUp(self):
    User.objects.create(username="samu", password='123', email="inventado@gmail.com")

  def test_return_token_if_user_exists(self):
    self.factory.get()