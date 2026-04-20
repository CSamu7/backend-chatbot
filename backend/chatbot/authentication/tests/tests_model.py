from django.test import TestCase
from ..models import User

class UserModelTestCase(TestCase):
  def setUp(self):
    User.objects.create(username="Samu", email="samuel.pdg@hotmail.com", password="123")

  def test_basic_user_when_is_created_is_not_super_user(self):
    user = User.objects.get(pk=1)

    self.assertIs(user.is_superuser, False)
