from django import forms
from django.conf import settings
from jsonapi.api import API
from jsonapi.resource import Resource

from .forms import UserForm, PostWithPictureForm

api = API()


@api.register
class UserResource(Resource):

    """ User Resource."""

    class Meta:
        model = settings.AUTH_USER_MODEL
        authenticators = [Resource.AUTHENTICATORS.SESSION]
        fieldnames_exclude = ['password']
        form = UserForm
        allowed_methods = 'GET', 'PUT', 'DELETE'


@api.register
class AuthorResource(Resource):

    """ Author Resource.

    Description for Author Resource.

    """

    class Meta:
        model = 'testapp.Author'
        allowed_methods = 'GET', 'POST', 'PUT', 'DELETE'

    @classmethod
    def clean_resources(cls, resources, request=None, **kwargs):
        if request.method == "POST":
            for resource in resources:
                if resource["name"] == "not clean name":
                    raise forms.ValidationError(
                        "Author name should not be 'not clean name'")
        return resources


@api.register
class PostWithPictureResource(Resource):
    class Meta:
        model = 'testapp.PostWithPicture'
        allowed_methods = 'GET', 'PUT'
        fieldnames_include = 'title_uppercased', 'dummy'
        fieldnames_exclude = 'title',
        form = PostWithPictureForm

    @staticmethod
    def dump_document_dummy(obj):
        return "dummy"


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

    @classmethod
    def get_filters(cls, filters):
        result = super(CommentResource, CommentResource).get_filters(filters)
        if 'is_outdated' in result:
            value = result.pop('is_outdated')
            if value:
                result['id__lt'] = 2
        return result


@api.register
class GroupResource(Resource):
    class Meta:
        model = 'testapp.Group'


@api.register
class MembershipResource(Resource):
    class Meta:
        model = 'testapp.Membership'
