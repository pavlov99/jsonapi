from jsonapi.resource import Resource
from jsonapi.api import API

api = API()


class PostResource(Resource):
    pass


api.register(PostResource)
