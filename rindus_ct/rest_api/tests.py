from django.test import TestCase
from rest_framework.test import APIClient

from definitions import RestCmd

class CrudTestCase(TestCase):

    def setUp(self):
        pass

    def test_create_posts(self):
        client = APIClient()

        data_post1 = {
            "userId": 1,
            "id": 1,
            "title": "first post",
            "body": "body of the first post"
        }

        response = client.post(RestCmd.POSTS.value, data_post1, format="json")