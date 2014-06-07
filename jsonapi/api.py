""" API manager implementation.

Responsible for routing and resource registration.

    from jsonapi.api import API
    from myapp.resources import PostResource, CommentResource

    api = API()
    api.register(PostResource)

    @api.register
    class ClientResource():
        ...

    then usage:
        url(r'^api/', include(api.urls)),


"""


class API(object):

    """ API handler."""

    def __init__(self):
        self.resource_map = dict()

    def register(self, resource):
        """ Register resource for currnet API."""
        self.resource_map[resource.Meta.name] = resource

    @property
    def urls(self):
        """ Get all of the api endpoints.

        NOTE: only for django as of now.
        NOTE: urlpatterns are deprecated since Django1.8

        :return list: urls

        """
        from django.conf.urls import url

        urls = []
        for resource_name, resource in self.resource_map.items():
            urls.extend([
                url(
                    r'^{0}/$'.format(resource_name),
                    lambda request, **kw: default_view(request, resource, **kw)
                ),
                url(
                    r'^{0}/(?P<id>[0-9]+)/$'.format(resource_name),
                    lambda request, **kw: default_view(request, resource, **kw)
                ),
            ])
        return urls


def default_view(request, resource, **kwargs):
    from django.http import HttpResponse
    items = resource.get(**kwargs)
    result = resource.Meta.name
    return HttpResponse(items)
