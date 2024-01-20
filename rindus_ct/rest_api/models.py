from django.db import models
from synchronization import SyncPost

default_user_id = 99999942

class Post(models.Model):
    owner = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE, null=True)
    userId = models.IntegerField(default=default_user_id)
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    body = models.TextField()

    def to_dict(self) -> dict:
        return {
            "userId": str(Post.userId),
            "id": str(Post.id),
            "title": str(Post.title),
            "body": str(Post.body)
        }

    def to_syncpost(self) -> SyncPost:
        return SyncPost(self)

class Comment(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    email = models.EmailField()
    body = models.TextField()

    def to_dict(self) -> dict:
        return {
            "postId": str(Comment.postId),
            "id": str(Comment.id),
            "name": str(Comment.name),
            "email": str(Comment.email),
            "body": str(Comment.body)
        }
