from ..serializers import UsersSerializer, LoginSerializer
from django.test import TestCase
from ..models import User

class LoginSerializerTestCase(TestCase):
  def test_login_is_succesful(self):
    serializer = LoginSerializer(data={"email": "test@gmail.com", "password": "123"})

    self.assertTrue(serializer.is_valid())
    self.assertEqual(0, len(serializer.errors))

  def test_login_fails_when_password_is_empty(self):
    serializer = LoginSerializer(data={"email": "test@gmail.com", "password": ""})

    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["password"])

  def test_login_fails_when_email_is_empty(self):
    serializer = LoginSerializer(data={"email": "", "password": "sadsad"})

    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["email"])

  def test_login_fails_when_email_is_invalid(self):
    serializer = LoginSerializer(data={"email": "testgmail.com", "password": "dad"})

    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["email"])

class UserSerializerTestCase(TestCase):
  def setUp(self):
    User.objects.create_user(email="test@gmail.com", password="123", username="sam")

  def test_email_already_exists(self):
    repeated_user = {
      'password': '123',
      'email':  'test@gmail.com',
      'username': 'sam'
    }

    serializer = UsersSerializer(data=repeated_user)
    serializer.is_valid()

    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["email"])

  def test_fail_when_email_is_not_valid(self):
    invalid_email_user = {
      'password': '123',
      'email': 'sam',
      'username': 'invalid'
    }

    serializer = UsersSerializer(data=invalid_email_user)
    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["email"])

  def test_fail_when_password_is_empty(self):
    not_password = {
      'password': '',
      'email': 'test@inventado.com',
      'username': 'invalid'
    }

    serializer = UsersSerializer(data=not_password)
    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["password"])


  def test_fail_when_username_is_empty(self):
    not_username = {
      'password': '3qrsdsfdsf',
      'email': 'test@inventado.com',
      'username': ''
    }

    serializer = UsersSerializer(data=not_username)
    self.assertFalse(serializer.is_valid())
    self.assertEqual(1, len(serializer.errors))
    self.assertIsNotNone(serializer.errors["username"])
