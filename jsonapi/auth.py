import base64
from django.contrib.auth import authenticate

from .utils import Choices


class SessionAuthenticator(object):
    @classmethod
    def authenticate(cls, request):
        user = request.user
        return user


class HTTPBasicAuthenticator(object):
    @classmethod
    def authenticate(cls, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                username, password = base64.b64decode(
                    auth[1]).decode('utf8').split(':')
                user = authenticate(username=username, password=password)
                return user


class DjangoToolkitOAuthAuthenticator(object):

    """ Authentication for django-oauth-toolkit library.

    NOTE: Authrntication requires django-oauth-toolkit to be installed.
    Usage:
        Use header "Authorization: Bearer <access_token>" with request.

    """

    @classmethod
    def authenticate(cls, request):
        from oauth2_provider.oauth2_backends import get_oauthlib_core
        oauthlib_core = get_oauthlib_core()
        valid, oauthlib_req = oauthlib_core.verify_request(request, scopes=[])
        if valid:
            return oauthlib_req.user
        else:
            return None


class Authenticator(object):

    AUTHENTICATORS = Choices(
        (SessionAuthenticator, 'SESSION'),
        (HTTPBasicAuthenticator, 'HTTP_BASIC'),
        (DjangoToolkitOAuthAuthenticator, 'DJANGO_TOOLKIT_OAUTH'),
    )

    class Meta:
        authenticators = []
        disable_get_authentication = None

    @classmethod
    def authenticate(cls, request):
        for authenticator in cls.Meta.authenticators:
            user = authenticator.authenticate(request)
            # if authenticater returns user with valid id, return it. NOTE:
            # request.user returns SimpleLazy object with is not False, but
            # might be AnonymousUser.
            if user and user.id:
                return user
