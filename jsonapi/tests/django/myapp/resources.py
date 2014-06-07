from jsonapi.resource import Resource
from jsonapi.api import API


class AuthorResource(Resource):
    class Meta:
        model = 'myapp.Author'


class PostWithPictureResource(Resource):
    class Meta:
        model = 'myapp.PostWithPicture'


api = API()
api.register(AuthorResource)
api.register(PostWithPictureResource)
