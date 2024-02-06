from django.core.management.base import BaseCommand

from ...synchronization import Synchronizer, sync_url
from ...definitions import RestCmd

class Command(BaseCommand):

    help = """Synchronizes remote api with database data"""

    def handle(self, *args, **kwargs):

        try:
            sync = Synchronizer(sync_url)
            result = sync.synchronize(RestCmd.POSTS)
            self.stdout.write(result)
            result = sync.synchronize(RestCmd.COMMENTS)
            self.stdout.write(result)
        except Exception as ex:
            self.stdout.write("Error loading data: " + str(ex))