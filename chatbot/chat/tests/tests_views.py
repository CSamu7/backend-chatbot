from rest_framework.test import APITestCase
from rest_framework import status

from authentication.models import User
from ..models import Chat

class ChatTestCase(APITestCase):
  def setUp(self):
    User.objects.create_user(username="samu", password="123", email="test@gmail.com")
    Chat.objects.create(user=User.objects.get(email="test@gmail.com"), title="Test 1")

    self.user = User.objects.get(email="test@gmail.com")
    self.client.login(email="test@gmail.com", password="123")

  def test_get_chats_relationated_with_user(self):
    response = self.client.get(f"/api/users/{self.user.pk}/chats/")
    chats = response.json()

    self.assertIs(status.HTTP_200_OK, response.status_code)
    self.assertTrue(all(chat['user'] == self.user.pk for chat in chats["results"]))

  def test_post_chat(self):
    chat = {"title": "test2", "user": self.user.pk}
    postResponse = self.client.post("/api/chats/", chat, format="json")

    self.assertIs(status.HTTP_201_CREATED, postResponse.status_code)

    getResponse = self.client.get(f"/api/users/{self.user.pk}/chats/")
    chats = getResponse.json()

    self.assertIs(status.HTTP_200_OK, getResponse.status_code)
    self.assertEqual(2, len(chats["results"]))

  def test_get_chat(self):
    response = self.client.get(f"/api/chats/1")
    chat = response.json()

    self.assertIs(status.HTTP_200_OK, response.status_code)
    self.assertEqual("Test 1", chat["title"])
    self.assertEqual(1, chat["user"])

  def put_chat(self):
    pass

  def test_delete_chat(self):
    response = self.client.delete(f"/api/chats/1")

    self.assertIs(status.HTTP_204_NO_CONTENT, response.status_code)

    response = self.client.get(f"/api/chats/1")
    self.assertIs(status.HTTP_404_NOT_FOUND, response.status_code)
