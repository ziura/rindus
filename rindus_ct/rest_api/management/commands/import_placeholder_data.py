from django.core.management.base import BaseCommand
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
import requests
import io

from ...models import Post, Comment
from ...serializers import PostSerializer, CommentSerializer

class Command(BaseCommand):
    _request_url = "https://jsonplaceholder.typicode.com"

    help = f"""Imports posts and comments resources from {_request_url}
            and loads them into the database"""


    def __is_data_loaded(self, cmd: str)-> bool:
        if cmd == "/posts":
            if Post.objects.all().count() > 0:
                return True
            else:
                return False
        elif cmd == "/comments":
            if Comment.objects.all().count() > 0:
                return True
            else:
                return False
        else:
            raise Exception(f"unknown API command {cmd}")


    def __load_data(self, cmd: str):
        if self.__is_data_loaded(cmd):
            self.stdout.write(
                f"{cmd} data already loaded. We need an empty table to load new data"
            )
            return

        url = Command._request_url + cmd
        res = requests.get(url)
        stream = io.BytesIO(res.content)
        data = JSONParser().parse(stream)
        
        if len(data) == 0:
            self.stdout.write("No data loaded. Empty set.")
            return

        for index, dataitem in enumerate(data):
            if cmd == "/posts":
                serializer = PostSerializer(data=dataitem)
            elif cmd == "/comments":
                serializer = CommentSerializer(data=dataitem)
            else:
                raise Exception(f"unknown API command {cmd}")

            if not serializer.is_valid():
                self.stdout.write(
                    f"Errors parsing post {index}: " + str(serializer.error_messages)
                )
                continue
            serializer.save()

        self.stdout.write(f"Finished loading data from {cmd}")

    def handle(self, *args, **kwargs):
        self.stdout.write(f"Requesting data to {Command._request_url}")

        try:
            self.__load_data("/posts")
            self.__load_data("/comments")
        except ParseError as ex:
            self.stdout.write("Could not parse downloaded data: " + str(ex))
        except Exception as ex:
            self.stdout.write("Error loading data: " + str(ex))