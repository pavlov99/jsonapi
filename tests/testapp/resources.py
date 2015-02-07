from django.conf import settings
from jsonapi.resource import Resource
from jsonapi.api import API

api = API()


@api.register
class UserResource(Resource):
    class Meta:
        model = settings.AUTH_USER_MODEL
        authenticators = [Resource.AUTHENTICATORS.SESSION]
        fieldnames_exclude = 'password',


@api.register
class AuthorResource(Resource):
    class Meta:
        model = 'testapp.Author'
        allowed_methods = 'GET', 'POST', 'PUT', 'DELETE'


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
    def dump_document_title(obj):
        return obj.title


@api.register
class CommentResource(Resource):
    class Meta:
        model = 'testapp.Comment'
        page_size = 3
