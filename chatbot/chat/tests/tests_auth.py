from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import User
from ..models import Chat

class AuthChatTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    User.objects.create_user(username="samu", password="123", email="test@gmail.com")
    User.objects.create_user(username="test", password="456", email="there@gmail.com")
    cls.user = User.objects.get(email="test@gmail.com")
    user2 = User.objects.get(email="there@gmail.com")
    
    #For some reason its overwritten.
    cls.client = APIClient()

    cls.list_chat_url = reverse('chat-list', kwargs={'pk': cls.user.pk})
    Chat.objects.create(user=cls.user, title="Test 1", pk = 1)
    Chat.objects.create(user=cls.user, title="Test 2", pk = 2)
    Chat.objects.create(user=user2, title="Test 3", pk = 3)

  def setUp(self):
    self.client.force_login(self.user)

  #Happy cases
  def test_get_chats_relationated_with_user(self):
    sut = self.client.get(self.list_chat_url)
    chats = sut.json()

    self.assertEqual(status.HTTP_200_OK, sut.status_code)
    self.assertTrue(all(chat['user'] == self.user.pk for chat in chats["results"]))
    self.assertTrue(2, len(chats["results"]))

  def test_post_chat(self):
    chat = {"title": "Test 3", "user": self.user.pk}
    url = reverse('chat-post')
    sut = self.client.post(url, chat, format="json")

    self.assertEqual(status.HTTP_201_CREATED, sut.status_code)

    response = self.client.get(self.list_chat_url)
    chats = response.json()

    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(3, chats["count"])

  def test_get_chat(self):
    url = reverse('chat-detail', kwargs={'pk': 1})
    response = self.client.get(url)
    chat = response.json()

    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual("Test 1", chat["title"])
    self.assertEqual(1, chat["id"])
    self.assertEqual(1, chat["user"])

  def test_delete_chat(self):
    url = reverse('chat-detail', kwargs={'pk': 2})
    sut = self.client.delete(url)
    self.assertIs(status.HTTP_204_NO_CONTENT, sut.status_code)

    response = self.client.get(f"/api/chats/2")
    self.assertIs(status.HTTP_404_NOT_FOUND, response.status_code)

  def test_prevent_get_chat_from_another_user(self):
    url = reverse('chat-detail', kwargs={'pk': 3})
    sut = self.client.get(url)

    self.assertEqual(status.HTTP_401_UNAUTHORIZED, sut.status_code)
    
  def test_prevent_delete_from_another_user(self):
    url = reverse('chat-detail', kwargs={'pk': 3})
    sut = self.client.get(url)

    self.assertEqual(status.HTTP_401_UNAUTHORIZED, sut.status_code)