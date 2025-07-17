from ..serializers import UsersSerializer
from django.test import TestCase

class UserSerializerTestCase(TestCase):
  def test_fail_when_email_is_not_valid(self):
    invalid_email_user = {
      'password': '123',
      'email': 'sam',
      'username': 'invalid'
    }

    serializer = UsersSerializer(data=invalid_email_user)
    self.assertIs(serializer.is_valid(), False)
