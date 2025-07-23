from rest_framework.test import APIRequestFactory, APIClient, force_authenticate
from rest_framework import status
from django.test import TestCase
import core.utils as utils

from authentication.models import User
from ..models import Chat

class ChatTestCase(TestCase):
  request_factory = APIRequestFactory()

  def setUp(self):
    User.objects.create_user(username="samu", password="123", email="inventado@gmail.com")
    Chat.objects.create(user=User.objects.get(email="inventado@gmail.com"), title="Test 1")

  def test_display_only_chats_relationated_with_user(self):
    user = User.objects.get(email="inventado@gmail.com")
    token = utils.get_token_for_user(user)

    headers = {
      "Authorization": f"Bearer {token["access"]}"
    }

    response = self.client.get(f"/api/users/{user.pk}/chats/", headers=headers)
    chats = response.json()
    self.assertIs(200, status.HTTP_200_OK)
    self.assertTrue(all(chat['user'] == user.pk for chat in chats["results"]))