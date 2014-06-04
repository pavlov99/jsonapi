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
#from django.conf.urls import url


class API(object):

    """ API handler."""

    def __init__(self, version=None, prefix=None):
        self.version = str(version)
        self.prefix = prefix or ""
        self.resource_map = dict()

    def register(self, resource):
        """ Register resource for currnet API."""
        self.resource_map[resource.Meta.name] = resource

    @property
    def urls(self):
        """ Get all of the api endpoints.

        NOTE: urlpatterns are deprecated since Django1.8

        :return list: urls

        """
        urls = []
        return urls
