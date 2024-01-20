from django.db import models

default_user_id = 99999942

class Post(models.Model):
    owner = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE, null=True)
    userId = models.IntegerField(default=default_user_id)
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    body = models.TextField()

class Comment(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    email = models.EmailField()
    body = models.TextField()
