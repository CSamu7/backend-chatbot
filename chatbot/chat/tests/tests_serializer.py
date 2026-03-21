from django.test import TestCase
from ..serializers import MessageSerializer, ChatSerializer
from authentication.models import User
from ..models import Chat

class ChatSerializerTests(TestCase):
  @classmethod
  def setUpTestData(cls):
    User.objects.create_user(username="samu", password="123", email="test@gmail.com")
  
  def test_chat_is_valid(self):
    data = {"title": "Yo jamas llore", "created_at": "2026-03-18 22:58", "user": 1}
    serializer = ChatSerializer(data=data)

    self.assertTrue(serializer.is_valid())
    self.assertEqual(0, len(serializer.errors))

  def test_fails_if_title_is_empty(self):
    data = {"title": "", "created_at": "2026-03-18 22:58", "user": 1}
    serializer = ChatSerializer(data=data)

    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))   
    self.assertIsNotNone(serializer.errors["title"])

class MessageSerializerTests(TestCase):
  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(username="samu", password="123", email="test@gmail.com")
    Chat.objects.create(user=cls.user, title="Test 1", pk = 1)

  def test_message_is_valid(self):
    serializer = MessageSerializer(data={'user': self.user.pk, 'text': "November Rain", 'send_at': "2026-03-18 22:58", 'chat': 1})

    self.assertTrue(serializer.is_valid())

  def test_return_404_if_message_is_empty(self):
    serializer = MessageSerializer(data={'user': self.user.pk, 'text': "", 'send_at': "2026-03-18 22:58", 'chat': 1})

    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["text"])