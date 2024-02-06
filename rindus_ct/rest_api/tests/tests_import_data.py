from rest_framework import status

from .tests_auth import AuthenticatedTestCase
from ..definitions import RestCmd, ImporterCodes
from ..management.commands.import_placeholder_data import DataImporter, sync_url
from ..management.commands.clear_data import DataClearer

#If the test engine fails to create the test database running the tests, 
# open the postgres shell and run:
# ALTER USER rindus CREATEDB;


class DataImportTestCase(AuthenticatedTestCase):

    def setUp(self):
        return super().setUp()

    def tearDown(self):
        DataClearer().clear_db_data()

    def test_import_placeholder_data(self):
        """
        Check that placeholder data is loaded to the database
        and deleted with proper commands
        """
        importer = DataImporter(sync_url)
        
        response_msg = importer.load_data(RestCmd.POSTS.value)
        self.assertEqual(response_msg, ImporterCodes.SUCCESS.value)

        response_msg = importer.load_data(RestCmd.COMMENTS.value)
        self.assertEqual(response_msg, ImporterCodes.SUCCESS.value)

        response = self.client.get(RestCmd.POSTS.value + "1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

        clearer = DataClearer()
        response_msg = clearer.clear_db_data()
        self.assertEqual(response_msg, ImporterCodes.DELETE_SUCCESS.value)

        response = self.client.get(RestCmd.POSTS.value + "1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_duplicate_data(self):
        """
        Check that the import command doesn't allow to import the data if
        it is already loaded
        """
        importer = DataImporter(sync_url)
        
        response_msg = importer.load_data(RestCmd.POSTS.value)
        self.assertEqual(response_msg, ImporterCodes.SUCCESS.value)

        response_msg = importer.load_data(RestCmd.COMMENTS.value)
        self.assertEqual(response_msg, ImporterCodes.SUCCESS.value)
        
        response_msg = importer.load_data(RestCmd.POSTS.value)
        self.assertEqual(response_msg, ImporterCodes.DUPLICATED.value)

        response_msg = importer.load_data(RestCmd.COMMENTS.value)
        self.assertEqual(response_msg, ImporterCodes.DUPLICATED.value)
