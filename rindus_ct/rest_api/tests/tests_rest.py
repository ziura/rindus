from rest_framework.test import APITestCase
from rest_framework import status
import json

from ..definitions import RestCmd
from ..models import Post, Comment, default_user_id

#If the test engine fails to create the test database running the tests, 
# open the postgres shell and run:
# ALTER USER rindus CREATEDB;


class CrudTestCase(APITestCase):

    def setUp(self):
        self.default_user_id = default_user_id

        self.post_id = 1
        Post.objects.create(
            userId=self.default_user_id,
            id=self.post_id,
            title="title",
            body="body"
        )

        self.comment_id = 1
        Comment.objects.create(
            postId=Post.objects.get(id=self.post_id),
            id=self.comment_id,
            name="comment",
            email="test@test.com",
            body="body"
        )

        return super().setUp()

    def test_create_posts(self):
        """
        Check that posts and comments are created and retrieved
        """
        post_id = self.post_id + 1
        post = {
            "userId": self.default_user_id,
            "id": post_id,
            "title": "first post",
            "body": "body",
        }

        response = self.client.post(RestCmd.POSTS.value, post)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(RestCmd.POSTS.value + str(post_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, post)

        comment_id = self.comment_id + 1
        comment = {
            "postId": post_id,
            "id": comment_id,
            "name": "name",
            "email": "test@test.com",
            "body": "body"
        }

        response = self.client.post(RestCmd.COMMENTS.value, comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(RestCmd.COMMENTS.value + str(comment_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, comment)

    def test_put(self):
        """
        Check that posts and comments updated with PUT commands
        """
        post = {
            "userId": self.default_user_id,
            "id": self.post_id,
            "title": "updated title",
            "body": "updated body",
        }

        response = self.client.put(RestCmd.POSTS.value + str(self.post_id) + "/", post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(RestCmd.POSTS.value + str(self.post_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, post)

        comment = {
            "postId": self.post_id,
            "id": self.comment_id,
            "name": "updated name",
            "email": "updatedtest@test.com",
            "body": "updated body"
        }

        response = self.client.put(RestCmd.COMMENTS.value + str(self.comment_id) + "/", comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(RestCmd.COMMENTS.value + str(self.comment_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, comment)

    def test_patch(self):
        """
        Check that posts and comments updated with PATCH commands
        """
        patch = {"title": "patched title"}

        response = self.client.patch(RestCmd.POSTS.value + str(self.post_id) + "/", patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(RestCmd.POSTS.value + str(self.post_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "patched title")

        patch = {"name": "patched name"}

        response = self.client.patch(RestCmd.COMMENTS.value + str(self.comment_id) + "/", patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(RestCmd.COMMENTS.value + str(self.comment_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "patched name")

    def test_cascade_on_delete(self):
        """
        Check that related comments are deleted when a post is deleted.
        Check that getting non-existing posts and comments return not found response
        """
        response = self.client.get(RestCmd.POSTS.value + str(self.post_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(RestCmd.COMMENTS.value + str(self.comment_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(RestCmd.POSTS.value + str(self.post_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(RestCmd.POSTS.value + str(self.post_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(RestCmd.COMMENTS.value + str(self.comment_id) + "/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_overwrite_existing(self):
        """
        Trying to create items with existing primary keys return error
        """
        post_id = self.post_id
        post = {
            "userId": self.default_user_id,
            "id": post_id,
            "title": "first post",
            "body": "body",
        }
        response = self.client.post(RestCmd.POSTS.value, post)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"id":["post with this id already exists."]})

        comment_id = self.comment_id
        comment = {
            "postId": post_id,
            "id": comment_id,
            "name": "name",
            "email": "test@test.com",
            "body": "body"
        }
        response = self.client.post(RestCmd.COMMENTS.value, comment)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"id":["comment with this id already exists."]})

    def test_email_validation(self):
        """
        Incorrect email formats must return format error
        """
        comment = {
            "postId": self.post_id,
            "id": self.comment_id,
            "name": "updated name",
            "email": "invalid-email-format",
            "body": "updated body"
        }

        response = self.client.put(RestCmd.COMMENTS.value + str(self.comment_id) + "/", comment)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"email":["Enter a valid email address."]})

    def test_unknown_field_validation(self):
        """
        Unknown json fields are validated and rejected in POST, PUT and PATCH requests
        """
        post_id = self.post_id + 1
        post = {
            "userId": self.default_user_id,
            "id": post_id,
            "title": "first post",
            "body": "body",
            "unknown": "unknown"
        }
        response = self.client.post(RestCmd.POSTS.value, post)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"non_field_errors":["Unknown field(s): unknown"]})
    
        comment = {
            "postId": self.post_id,
            "id": self.comment_id,
            "name": "updated name",
            "email": "updated@email.com",
            "body": "updated body",
            "unknown": "unknown field"
        }
        response = self.client.put(RestCmd.COMMENTS.value + str(self.comment_id) + "/", comment)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"non_field_errors":["Unknown field(s): unknown"]})

        patch = {"unknown": "unknown field"}
        response = self.client.patch(RestCmd.COMMENTS.value + str(self.comment_id) + "/", patch)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"non_field_errors":["Unknown field(s): unknown"]})