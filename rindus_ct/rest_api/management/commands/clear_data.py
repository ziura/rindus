from django.core.management.base import BaseCommand
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
import requests
import io

from ...models import Post, Comment
from ...serializers import PostSerializer, CommentSerializer

class Command(BaseCommand):

    help = """Deletes all saved data from the database"""

    def handle(self, *args, **kwargs):

        try:
            Post.objects.all().delete()
            Comment.objects.all().delete()
            self.stdout.write("Data deleted from the database")
        except Exception as ex:
            self.stdout.write("Error loading data: " + str(ex))