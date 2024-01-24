from django.core.management.base import BaseCommand
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
import requests
import io

from ...definitions import RestCmd, ImporterCodes
from ...models import Post, Comment
from ...serializers import PostSerializer, CommentSerializer
from ...synchronization import Requester, sync_url


class DataImporter():

    def __init__(self, url: str):
        self.__request_url = sync_url

    def __is_data_loaded(self, cmd: str)-> bool:
        if cmd == RestCmd.POSTS.value:
            if Post.objects.all().count() > 0:
                return True
            else:
                return False
        elif cmd == RestCmd.COMMENTS.value:
            if Comment.objects.all().count() > 0:
                return True
            else:
                return False
        else:
            raise Exception(f"unknown API command {cmd}")


    def load_data(self, cmd: str):
        if self.__is_data_loaded(cmd):
            return ImporterCodes.DUPLICATED.value

        requester = Requester(self.__request_url)
        data = requester.data_list_from_get_request(cmd)
        
        if len(data) == 0:
            return ImporterCodes.EMPTY.value

        for index, dataitem in enumerate(data):
            if cmd == RestCmd.POSTS.value:
                serializer = PostSerializer(data=dataitem)
            elif cmd == RestCmd.COMMENTS.value:
                serializer = CommentSerializer(data=dataitem)
            else:
                raise Exception(f"unknown API command {cmd}")

            if not serializer.is_valid():
                return f"Errors parsing item {index}: " + str(serializer.errors)

            serializer.save()

        return ImporterCodes.SUCCESS.value


class Command(BaseCommand):
    help = f"""Imports posts and comments resources from {sync_url}
            and loads them into the database"""

    def handle(self, *args, **kwargs):
        self.stdout.write(f"Requesting data to {sync_url}")

        try:
            importer = DataImporter(sync_url)

            result_msg = importer.load_data(RestCmd.POSTS.value)
            self.stdout.write(RestCmd.POSTS.value + ": " + result_msg)
            result_msg = importer.load_data(RestCmd.COMMENTS.value)
            self.stdout.write(RestCmd.COMMENTS.value + ": " + result_msg)

        except ParseError as ex:
            self.stdout.write("Could not parse downloaded data: " + str(ex))
        except Exception as ex:
            self.stdout.write("Error loading data: " + str(ex))


