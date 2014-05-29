""" API manager implementation.

Responsible for routing and resource registration.

    from jsonapi.api import API
    from myapp.resources import PostResource, CommentResource

    api = API()
    api.register(PostResource)

    @api.register
    class ClientResource():
        ...

"""
from django.conf.urls import url


class API(object):

    def __init__(self, version=None, prefix=None):
        self.version = str(version)
        self.prefix = prefix or ""
        self.resource_map = dict()

    def register(self, resource):
        """ Register resource for currnet API."""
        self.resource_map[len(self.resource_map)] = resource

    @property
    def urls(self):
        # NOTE: urlpatterns are deprecated since Django1.8
        urls = []
        return urls
