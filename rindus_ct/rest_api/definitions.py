from enum import Enum

class RestCmd(Enum):
    POSTS = "/posts/"
    COMMENTS = "/comments/"

class ImporterCodes(Enum):
    SUCCESS = "Finished loading data successfully"
    DUPLICATED = "Data already loaded. We need an empty table to load new data"
    EMPTY = "No data loaded. Empty set."
    DELETE_SUCCESS = "Data successfully deleted from database"