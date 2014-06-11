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
import logging
logger = logging.getLogger(__name__)


class API(object):

    """ API handler."""

    def __init__(self):
        self.resource_map = dict()
        self._resource_relations = None

    @property
    def model_resource_map(self):
        return {
            resource.Meta.model: resource
            for resource in self.resource_map.values()
            if hasattr(resource.Meta, 'model')
        }

    def register(self, resource=None):
        """ Register resource for currnet API.

        :return jsonapi.resource.Resource: resource

        """
        if resource is None:
            def wrapper(resource):
                return self.register(resource)
            return wrapper

        if resource.Meta.name in self.resource_map:
            raise ValueError('Resource {} already registered'.format(
                resource.Meta.name))

        if resource.Meta.name_plural in self.resource_map:
            raise ValueError(
                'Resource plural name {} conflicts with registered resource'.
                format(resource.Meta.name))

        resource_plural_names = {
            r.Meta.name_plural for r in self.resource_map.values()
        }
        if resource.Meta.name in resource_plural_names:
            raise ValueError(
                'Resource name {} conflicts with other resource plural name'.
                format(resource.Meta.name)
            )

        self.resource_map[resource.Meta.name] = resource
        resource.Meta.api = self
        return resource

    @property
    def urls(self):
        """ Get all of the api endpoints.

        NOTE: only for django as of now.
        NOTE: urlpatterns are deprecated since Django1.8

        :return list: urls

        """
        from django.conf.urls import url

        urls = [
            url(r'^$', self.map_view),
            url(r'^(?P<resource_name>\w+)/$', self.default_view),
            url(r'^(?P<resource_name>\w+)/(?P<id>[0-9]+)/$',
                self.default_view),
        ]
        #urls.extend([
            #url(r'^(?P<resource_name>\w+)/((?P<id>[0-9]+)/)?$', self.test_view)
        #])

        #urls.extend([
            ##url(r'^(?P<resource_name>{})/$'.format(resource_name), self.test_view)
            #url(r'^(?P<resource_name>\w+)/$', self.test_view),
            #url(r'^(?P<resource_name>\w+)/(?P<resource_id>\w+)/$', self.test_view),
            ##for resource_name in self.resource_map
        #])
        return urls

    def test_view(self, request, *args, **kwargs):
        from django.http import HttpResponse
        print("Test View: ", args, kwargs)
        #import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        pass
        return HttpResponse(str(args) + str(kwargs))

    def map_view(self, request):
        """ Show information about available resources.

        :return django.http.HttpResponse

        """
        from django.http import HttpResponse
        import json

        resource_info = {
            "resources": [{
                "id": index + 1,
                "href": "{}://{}/api/{}/".format(
                    request.META['wsgi.url_scheme'],
                    request.META['HTTP_HOST'],
                    resource_name
                ),
            } for index, resource_name in enumerate(self.resource_map)]
        }
        response = json.dumps(resource_info)
        return HttpResponse(response, content_type="application/vnd.api+json")

    def default_view(self, request, resource_name, **kwargs):
        """ Handler for resources.

        :return django.http.HttpResponse

        """
        resource = self.resource_map[resource_name]
        from django.http import HttpResponse
        items = resource.get(**kwargs)
        return HttpResponse(items, content_type="application/vnd.api+json")
