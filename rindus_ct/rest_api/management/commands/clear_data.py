from django.core.management.base import BaseCommand
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
import requests
import io

from ...models import Post, Comment
from ...serializers import PostSerializer, CommentSerializer
from ...definitions import ImporterCodes

class DataClearer():

    def clear_db_data(self):
        Post.objects.all().delete()
        Comment.objects.all().delete()
        return ImporterCodes.DELETE_SUCCESS.value

class Command(BaseCommand):

    help = """Deletes all saved data from the database"""

    def handle(self, *args, **kwargs):

        try:
            self.stdout.write( DataClearer().clear_db_data() )
        except Exception as ex:
            self.stdout.write("Error loading data: " + str(ex))