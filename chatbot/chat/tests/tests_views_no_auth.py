from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import User
from ..models import Chat
from django.core.exceptions import ObjectDoesNotExist

class NoAuthTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    User.objects.create_user(username="samu", password="123", email="test@gmail.com")
    cls.user = User.objects.get(email="test@gmail.com")
    cls.client = APIClient()

    Chat.objects.create(user=cls.user, title="Test 1", pk = 1)
    Chat.objects.create(user=cls.user, title="Test 2", pk = 2)

  def test_get_all_return_401(self):
    sut = self.client.get(f"/api/users/{self.user.pk}/chats/")

    self.assertEqual(status.HTTP_401_UNAUTHORIZED, sut.status_code)

  def test_post_returns_401(self):
    chat = {"title": "Test 3", "user": self.user.pk}
    sut = self.client.post("/api/chats/", chat, format="json")

    self.assertEqual(status.HTTP_401_UNAUTHORIZED, sut.status_code)
    self.assertRaises(ObjectDoesNotExist, lambda: Chat.objects.get(pk = 3))

  def test_get_returns_401(self):
    url = reverse('chat-detail', kwargs={'pk': 1})
    response = self.client.get(url)

    self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

  def test_delete_chat(self):
    sut = self.client.delete(f"/api/chats/2")
    self.assertEqual(status.HTTP_401_UNAUTHORIZED, sut.status_code)

    chat = Chat.objects.get(pk = 2)
    self.assertIsNotNone(chat)
