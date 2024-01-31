from rest_framework.parsers import JSONParser
import requests
import io

from .models import Post, Comment
from .definitions import RestCmd, SyncCodes

sync_url = "https://jsonplaceholder.typicode.com"


class SyncPost():
    def __init__(self, post: Post):
        self.userId = post.userId
        self.id = post.id
        self.title = post.title
        self.body = post.body

    def __repr__(self):
        return f"""SyncPost(
                userId={self.userId},
                id={self.id},
                title='{self.title}',
                body='{self.body}')"""

    def __eq__(self, other):
        if isinstance(other, SyncPost):
            return (
                (self.userId == other.userId) and
                (self.id == other.id) and
                (self.title == other.title) and
                (self.body == other.body)
            )
        else:
            return False
        
    def __ne__(self, other):
        return (not self.__eq__(other))
    
    def __hash__(self):
        return hash(self.__repr__())

    @classmethod
    def from_dict(cls, dict_post: dict):
        return cls(
            Post(
                userId=dict_post["userId"],
                id=dict_post["id"],
                title=dict_post["title"],
                body=dict_post["body"]
            )
        )

    def to_dict(self) -> dict:
        return {
            "userId": str(Post.userId),
            "id": str(Post.id),
            "title": str(Post.title),
            "body": str(Post.body)
        }


class SyncComment():
    def __init__(self, comment: Comment):
        self.postId = comment.postId
        self.id = comment.id
        self.name = comment.name
        self.email = comment.email
        self.body = comment.body

    def __repr__(self):
        return f"""SyncComment(
                postId={self.postId},
                id={self.id},
                name='{self.name}',
                email='{self.email}'),
                body='{self.body}'"""

    def __eq__(self, other):
        if isinstance(other, SyncComment):
            return (
                (self.postId == other.postId) and
                (self.id == other.id) and
                (self.name == other.name) and
                (self.email == other.email) and
                (self.body == other.body)
            )
        else:
            return False
        
    def __ne__(self, other):
        return (not self.__eq__(other))
    
    def __hash__(self):
        return hash(self.__repr__())

    @classmethod
    def from_dict(cls, dict_comment: dict):
        try:
            post = Post.objects.get(id=int(dict_comment["postId"]))
        except Post.DoesNotExist:
            post = None

        return cls(
            Comment(
                postId=post,
                id=dict_comment["id"],
                name=dict_comment["name"],
                email=dict_comment["email"],
                body=dict_comment["body"]
            )
        )

    def to_dict(self) -> dict:
        return {
            "postId": str(Comment.postId),
            "id": str(Comment.id),
            "name": str(Comment.name),
            "email": str(Comment.email),
            "body": str(Comment.body)
        }


class Requester():

    def __init__(self, url: str):
        self.__url = url

    def data_list_from_get_request(self, cmd: str) -> list:
        url = self.__url + cmd
        response = requests.get(url)
        stream = io.BytesIO(response.content)
        return JSONParser().parse(stream)
    
    def delete(self, cmd: str):
        url = self.__url + cmd
        requests.delete(url)

    def create(self, cmd: str, content: dict):
        url = self.__url + cmd
        requests.post(url, json=content)

    def update(self, cmd: str, content: dict):
        url = self.__url + cmd
        requests.put(url, json=content)


class SynchronizerCRUD():

    def __init__(self, url, cmd):
        self.__cmd = cmd
        self.__request_url = url + cmd

    def delete_set(self, ds: set) -> str:
        if (len(ds) > 0):
            requester = Requester(self.__request_url)
            response = f", deleted ids:"
            for item in ds:
                delete_cmd = self.__request_url + str(item.id)
                requester.delete(delete_cmd)
                response += str(item.id) + " "
            return response
        return " 0 deleted "

    def create_set(self, ds: set) -> str:
        if (len(ds) > 0):
            requester = Requester(self.__request_url)
            response = f", created ids:"
            for item in ds:
                post_cmd = self.__request_url + str(item.id)
                requester.create(post_cmd, item.to_dict())
                response += str(item.id) + " "
            return response
        return " 0 created "
    
    def update_set(self, ds: set) -> str:
        if (len(ds) > 0):
            requester = Requester(self.__request_url)
            response = f", updated ids:"
            for item in ds:
                put_cmd = self.__request_url + str(item.id)
                requester.update(put_cmd, item.to_dict())
                response += str(item.id) + " "
            return response
        return " 0 updated "


class Synchronizer():

    def __init__(self, url: str):
        self.__request_url = url
        self.created = set()
        self.updated = set()
        self.deleted = set()

    def __compute_changes(self, set_db: set, set_rq: set):
        self.created, self.updated, self.deleted = set(), set(), set()

        for db_item in set_db:
            exists = False
            for rq_item in set_rq:
                if db_item.id == rq_item.id:
                    exists = True
            
            if exists:
                self.updated.add(db_item)
            else:
                self.created.add(db_item)

        for rq_item in set_rq:
            exists = False
            for db_item in set_db:
                if db_item.id == rq_item.id:
                    exists = True

            if not exists:
                self.deleted.add(rq_item)

    def __syncrhonize_remote(self, cmd: RestCmd, db_data: list, rq_data: list):
        """
        Calculates the difference between database and received data and syncrhonizes
        remote server according to the differences
        """
        set_db = set(db_data)
        set_rq = set(rq_data)
        
        if set_db == set_rq:
            return SyncCodes.NO_CHANGE.value

        rq_diff = set_rq.difference(set_db)
        db_diff = set_db.difference(set_rq)
        self.__compute_changes(db_diff, rq_diff)

        response = f"Synchronized {cmd.value}: "
        crud = SynchronizerCRUD(self.__request_url, cmd.value)
        response += crud.create_set(self.created)
        response += crud.delete_set(self.deleted)
        response += crud.update_set(self.updated)
        return response


    def synchronize(self, cmd: RestCmd) -> str:
        f"""
        Synchronizes the database in the project with data from {sync_url}
        """
        match cmd:
            case RestCmd.POSTS:
                sync_class = SyncPost
                model = Post
            case RestCmd.COMMENTS:
                sync_class = SyncComment
                model = Comment
            case _:
                return "Error. Undefined REST command."

        requester = Requester(self.__request_url)
        vrq_data = requester.data_list_from_get_request(cmd.value)
        rq_data = []
        for d in vrq_data:
            rq_data.append(sync_class.from_dict(d))

        data_list = list(model.objects.all())
        db_data = []
        for post in data_list:
            db_data.append(sync_class(post))

        return self.__syncrhonize_remote(cmd, db_data, rq_data)
