from django.conf import settings
from jsonapi.resource import Resource
from jsonapi.api import API

api = API()


@api.register
class UserResource(Resource):

    """ User Resource."""

    class Meta:
        model = settings.AUTH_USER_MODEL
        authenticators = [Resource.AUTHENTICATORS.SESSION]
        fieldnames_exclude = 'password',
        allowed_methods = 'GET', 'PUT'


@api.register
class AuthorResource(Resource):

    """ Author Resource.

    Description for Author Resource.

    """

    class Meta:
        model = 'testapp.Author'
        allowed_methods = 'GET', 'POST', 'PUT', 'DELETE'


@api.register
class PostWithPictureResource(Resource):
    class Meta:
        model = 'testapp.PostWithPicture'
        fieldnames_include = 'title_uppercased',
        fieldnames_exclude = 'title',


@api.register
class PostResource(Resource):
    class Meta:
        model = 'testapp.Post'
        allowed_methods = 'GET', 'POST'

    @staticmethod
    def dump_document_title(obj):
        return obj.title


@api.register
class CommentResource(Resource):
    class Meta:
        model = 'testapp.Comment'
        page_size = 3


@api.register
class GroupResource(Resource):
    class Meta:
        model = 'testapp.Group'


@api.register
class MembershipResource(Resource):
    class Meta:
        model = 'testapp.Membership'
