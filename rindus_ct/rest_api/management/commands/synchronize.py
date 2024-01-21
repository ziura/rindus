from django.core.management.base import BaseCommand
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
import requests
import io

from ...synchronization import Synchronizer, sync_url


class Command(BaseCommand):

    help = """Synchronizes remote api with database data"""

    def handle(self, *args, **kwargs):

        try:
            sync = Synchronizer(sync_url)
            result = sync.synchronize()
            self.stdout.write(result)
        except Exception as ex:
            self.stdout.write("Error loading data: " + str(ex))