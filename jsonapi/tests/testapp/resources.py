from jsonapi.resource import Resource
from jsonapi.api import API

api = API()


@api.register
class AuthorResource(Resource):
    class Meta:
        model = 'testapp.Author'


@api.register
class PostWithPictureResource(Resource):
    class Meta:
        model = 'testapp.PostWithPicture'
