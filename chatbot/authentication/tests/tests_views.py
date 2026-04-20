from rest_framework.test import  APIClient, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from ..models import User

class AuthViewTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    User.objects.create_user(username="samu", password="123", email="inventado@gmail.com")
    cls.client = APIClient()
    cls.getUserUrl = reverse('whoami')

    cls.loginUrl = reverse('login')
    cls.logoutUrl = reverse('logout')

  def test_login_returns_cookies_if_data_is_correct(self):
    body = {"email": "inventado@gmail.com", "password": "123"}

    sut = self.client.post(self.loginUrl, data=body, content_type="application/json")
    self.assertIs(sut.status_code, status.HTTP_200_OK)
    self.assertIsNotNone(sut.cookies["sessionid"])

  def get_401_if_login_is_invalid(self):
    response = self.client.post(self.loginUrl, data={"email": "inventado@gmail.com", "password": "12345454"})

    self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

  def test_create_new_user(self):
    data = {
      "username": "soynuevo",
      "email": "soynuevo@gmail.com",
      "password": "1234"
    }

    url = reverse('post-user')

    sut = self.client.post(url, data=data, content_type="application/json")
    user_created = User.objects.get(email="soynuevo@gmail.com")

    self.assertIs(sut.status_code, status.HTTP_201_CREATED)
    self.assertIsNotNone(user_created)
    self.assertEqual(user_created.email, "soynuevo@gmail.com")

  def test_logout(self):
    body = {"email": "inventado@gmail.com", "password": "123"}

    response = self.client.post(self.loginUrl, data=body, content_type="application/json")
    oldCookie = response.cookies.get("csrftoken")
    self.assertIsNotNone(oldCookie)

    sut = self.client.get(self.logoutUrl, cookie=oldCookie)

    recentCookie = sut.cookies.get("csrftoken")

    self.assertIsNone(recentCookie)

  def test_get_details_user_if_user_is_auth(self):
    user = User.objects.get(email="inventado@gmail.com")
    self.client.force_login(user)
    sut = self.client.get(self.getUserUrl)

    self.assertIs(sut.status_code, status.HTTP_200_OK)
  


