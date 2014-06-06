from .models import Author
from jsonapi.resource import Resource
from jsonapi.api import API


class AuthorResource(Resource):
    class Meta:
        model = Author


api = API()
api.register(AuthorResource)
print(api.urls)
