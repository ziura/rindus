from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['userId', 'id', 'title', 'body']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['postId', 'id', 'name', 'email', 'body']