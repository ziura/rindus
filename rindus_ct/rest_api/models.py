from django.db import models

class Post(models.Model):
    userId = models.IntegerField()
    title = models.TextField()
    body = models.TextField()

class Comment(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    email = models.EmailField()
    body = models.TextField()
