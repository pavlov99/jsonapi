from jsonapi.resource import Resource
from jsonapi.api import API

api = API()


@api.register
class AuthorResource(Resource):
    class Meta:
        model = 'testapp.Author'
        allowed_methods = 'get', 'create'


@api.register
class PostWithPictureResource(Resource):
    class Meta:
        model = 'testapp.PostWithPicture'
        fieldnames_include = 'title_uppercased',


@api.register
class PostResource(Resource):
    class Meta:
        model = 'testapp.Post'

    @staticmethod
    def dump_document_title(value):
        return value


@api.register
class CommentResource(Resource):
    class Meta:
        model = 'testapp.Comment'
        page_size = 3
