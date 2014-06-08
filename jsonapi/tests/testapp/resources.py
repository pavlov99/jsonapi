from jsonapi.resource import Resource
from jsonapi.api import API


class AuthorResource(Resource):
    class Meta:
        model = 'testapp.Author'


class PostWithPictureResource(Resource):
    class Meta:
        model = 'testapp.PostWithPicture'


api = API()
api.register(AuthorResource)
api.register(PostWithPictureResource)
