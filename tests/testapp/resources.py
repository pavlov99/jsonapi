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


@api.register
class PostResource(Resource):
    class Meta:
        model = 'testapp.Post'

    @staticmethod
    def dump_document_title(value):
        return value.capitalize()


@api.register
class CommentResource(Resource):
    class Meta:
        model = 'testapp.Comment'
