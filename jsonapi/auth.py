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


class Authenticator(object):

    AUTHENTICATORS = Choices(
        (SessionAuthenticator, 'SESSION'),
        (HTTPBasicAuthenticator, 'HTTP_BASIC'),
    )

    class Meta:
        authenticators = []

    @classmethod
    def authenticate(cls, request):
        for authenticator in cls.Meta.authenticators:
            user = authenticator.authenticate(request)
            if user:
                return user
