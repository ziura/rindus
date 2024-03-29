from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


#Change to AllowAny to disable authentication in requests
common_permission_level= permissions.IsAuthenticated


class PostsList(GenericAPIView):
    """
    Lists all posts or creates a new one
    """

    permission_classes = [common_permission_level]
    serializer_class = PostSerializer

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostsView(GenericAPIView):
    """
    Reads, updates or deletes single posts
    """

    permission_classes = [common_permission_level]
    serializer_class = PostSerializer

    def __get_post(self, pk) -> Post:
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        post = self.__get_post(pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.__get_post(pk=pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        post = self.__get_post(pk=pk)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.__get_post(pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsList(GenericAPIView):
    """
    Lists all comments or creates a new one
    """

    permission_classes = [common_permission_level]
    serializer_class = CommentSerializer

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsView(GenericAPIView):
    """
    Reads, updates or deletes single comments
    """

    permission_classes = [common_permission_level]
    serializer_class = CommentSerializer

    def __get_comment(self, pk) -> Comment:
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        comment = self.__get_comment(pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.__get_comment(pk=pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        comment = self.__get_comment(pk=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.__get_comment(pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
