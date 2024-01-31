from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Comment


class CommonSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        unknown =  set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError("Unknown field(s): {}".format(", ".join(unknown)))
        return attrs


class PostSerializer(CommonSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Post
        fields = ['owner', 'userId', 'id', 'title', 'body']


class CommentSerializer(CommonSerializer):
    class Meta:
        model = Comment
        fields = ['postId', 'id', 'name', 'email', 'body']



class UserSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'posts']