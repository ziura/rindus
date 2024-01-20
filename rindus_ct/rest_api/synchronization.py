from rest_framework.parsers import JSONParser
import requests
import io

from models import Post, Comment

sync_url = "https://jsonplaceholder.typicode.com"

class SyncPost():
    def __init__(self, post: Post):
        self.__userId = post.userId
        self.__id = post.id
        self.__title = post.title
        self.__body = post.body

    def __repr__(self):
        return f"""SyncPost(
                userId={self.__userId},
                id={self.__id},
                title='{self.__title}',
                body='{self.__body}')"""

    def __eq__(self, other):
        if isinstance(other, SyncPost):
            return (
                (self.__userId == other.userId) and
                (self.__id == other.id) and
                (self.__title == other.title) and
                (self.__body == other.body)
            )
        else:
            return False
        
    def __ne__(self, other):
        return (not self.__eq__(other))
    
    def __hash__(self):
        return hash(self.__repr__())


class Requester():

    def __init__(self, url: str):
        self.__url = url

    def data_list_from_get_request(self, cmd: str) -> list:
        url = self.__url + cmd
        response = requests.get(url)
        stream = io.BytesIO(response.content)
        return JSONParser().parse(stream)


class Synchronizer():
    _request_url = sync_url

    def __init__(self):
        pass

    def __syncrhonize_remote(self, db_data: list[SyncPost], rq_data: list[SyncPost]):
        pass

    def synchronize(self):
        f"""
        Synchronizes the database in the project with data from {sync_url}
        """

        requester = Requester(Synchronizer._request_url)
        vrq_data = requester.data_list_from_get_request("/posts")
        rq_data = []
        for d in vrq_data:
            rq_data.append(SyncPost.from_dict(d))

        data_list = list(Post.objects.all())
        db_data = []
        for post in data_list:
            db_data.append(post.to_syncpost())

        self.__syncrhonize_remote(db_data, rq_data)


