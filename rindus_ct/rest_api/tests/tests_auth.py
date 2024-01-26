from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from ..definitions import RestCmd

class AuthenticatedTestCase(APITestCase):
    """
    AuthenticatedTestCase is to be extended by test cases that require authenticated
    requests.
    """
    def setUp(self):

        name = "username"
        password = "1234"
        mail = "test@test.com"
        user = User.objects.create_user(username=name, email=mail, password=password)
        self.client.login(username=name, password=password)
        result = Token.objects.get_or_create(user=user)
        token = result[0]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        return super().setUp()

class AuthTestCase(APITestCase):

    def test_auth_401(self):
        """
        Test that requests not authorized are rejected with code 401
        """
        response = self.client.get(RestCmd.POSTS.value)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(RestCmd.COMMENTS.value)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        content = {"any": "any"}

        response = self.client.post(RestCmd.POSTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(RestCmd.COMMENTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(RestCmd.POSTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(RestCmd.COMMENTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(RestCmd.POSTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(RestCmd.COMMENTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(RestCmd.POSTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(RestCmd.COMMENTS.value + "1/", data=content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
