from rest_framework.test import APITestCase
from rest_framework import status
import json

from ..definitions import RestCmd, SyncCodes
from ..models import Post, Comment, default_user_id
from ..synchronization import Synchronizer, sync_url
from ..management.commands.clear_data import DataClearer
from ..management.commands.import_placeholder_data import DataImporter

#If the test engine fails to create the test database running the tests, 
# open the postgres shell and run:
# ALTER USER rindus CREATEDB;


class CrudTestCase(APITestCase):

    def setUp(self):
        importer = DataImporter(sync_url)
        importer.load_data(RestCmd.POSTS.value)
        importer.load_data(RestCmd.COMMENTS.value)

        return super().setUp()

    def tearDown(self):
        DataClearer().clear_db_data()

    def test_synchronize_no_change(self):
        """
        Check that synchronization does not happen if there are no 
        changes to the database after the synchronization
        """
        sync = Synchronizer(sync_url)
        result = sync.synchronize(RestCmd.POSTS)
        self.assertEqual(result, SyncCodes.NO_CHANGE.value)
        result = sync.synchronize(RestCmd.COMMENTS)
        self.assertEqual(result, SyncCodes.NO_CHANGE.value)

    def test_synchronize_crud(self):
        """
        Check that created, updated, and deleted posts and comments
        are synchronized with the remote API Rest interface
        """
        post_created = Post.objects.all().count() + 1
        comment_created = Comment.objects.all().count() + 1
        post = Post.objects.create(
            userId=default_user_id,
            id=post_created,
            title="test title",
            body="test body"
        )
        comment = Comment.objects.create(
            postId=post,
            id=comment_created,
            name="test",
            email="test@test.com",
            body="comment body"
        )

        post_deleted = 1
        post = Post.objects.get(id=post_deleted)
        comments = Comment.objects.filter(postId=post)
        comments_deleted = []
        for c in comments:
            comments_deleted.append(c.id)
        post.delete()
        #Related comments are deleted on cascade from deleting the post


        post_updated = 2
        post = Post.objects.get(id=post_updated)
        comment = Comment.objects.filter(postId=post).first()
        comment_updated = comment.id
        post.body = "updated test body"
        comment.body = "updated test body"
        post.save()
        comment.save()

        sync = Synchronizer(sync_url)
        sync.synchronize(RestCmd.POSTS)
        self.assertEqual(len(sync.created), 1)
        self.assertEqual(len(sync.updated), 1)
        self.assertEqual(len(sync.deleted), 1)
        self.assertEqual( next(iter(sync.created)).id, post_created )
        self.assertEqual( next(iter(sync.updated)).id, post_updated )
        self.assertEqual( next(iter(sync.deleted)).id, post_deleted )

        sync.synchronize(RestCmd.COMMENTS)
        self.assertEqual( next(iter(sync.created)).id, comment_created )
        self.assertEqual( next(iter(sync.updated)).id, comment_updated )

        for comment in sync.deleted:
            self.assertEqual( comment.id in comments_deleted, True )