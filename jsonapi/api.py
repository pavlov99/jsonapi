""" API manager implementation.

Responsible for routing and resource registration.

.. code-block:: python

    # resources.py
    from jsonapi.api import API
    from jsonapi.resource import Resource

    api = API()

    @api.register
    class AuthorResource(Resource):
        class Meta:
            model = 'testapp.author'

    # urls.py
    urlpatterns = patterns(
        '',
        url(r'^api', include(api.urls))
    )

"""
from django.http import HttpResponse, HttpResponseNotAllowed
import logging
import json

from .utils import Choices
from .model_inspector import ModelInspector

logger = logging.getLogger(__name__)


class API(object):

    """ API handler."""

    HTTP_METHODS = Choices(
        ('GET', 'get'),
        ('POST', 'create'),
        ('PUT', 'update'),
        ('DELETE', 'delete'),
    )
    CONTENT_TYPE = "application/vnd.api+json"

    def __init__(self):
        self._resources = []
        self.base_url = None  # base server url
        self.api_url = None  # api root url
        self.model_inspector = ModelInspector()
        self.model_inspector.inspect()

    @property
    def resource_map(self):
        """ Resource map of api.

        .. versionadded:: 0.4.1

        :return: resource name to resource mapping.
        :rtype: dict

        """
        return {r.Meta.name: r for r in self._resources}

    @property
    def model_resource_map(self):
        return {
            resource.Meta.model: resource
            for resource in self.resource_map.values()
            if hasattr(resource.Meta, 'model')
        }

    def register(self, resource=None, **kwargs):
        """ Register resource for currnet API.

        :param resource: Resource to be registered
        :type resource: jsonapi.resource.Resource or None
        :return: resource
        :rtype: jsonapi.resource.Resource

        .. versionadded:: 0.4.1
        :param kwargs: Extra meta parameters

        """
        if resource is None:
            def wrapper(resource):
                return self.register(resource, **kwargs)
            return wrapper

        for key, value in kwargs.items():
            setattr(resource.Meta, key, value)

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

        resource.Meta.api = self
        self._resources.append(resource)
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
        ]

        for resource_name in self.resource_map:
            urls.extend([
                url(r'/(?P<resource_name>{})$'.format(
                    resource_name), self.handler_view),
                url(r'/(?P<resource_name>{})/(?P<ids>[\w\-\,]+)$'.format(
                    resource_name), self.handler_view),
            ])

        return urls

    def update_urls(self, request, resource_name=None, ids=None):
        """ Update url configuration.

        :param request:
        :param resource_name:
        :type resource_name: str or None
        :param ids:
        :rtype: None

        """
        http_host = request.META.get('HTTP_HOST', None)

        if http_host is None:
            http_host = request.META['SERVER_NAME']
            if request.META['SERVER_PORT'] not in ('80', '443'):
                http_host = "{}:{}".format(
                    http_host, request.META['SERVER_PORT'])

        self.base_url = "{}://{}".format(
            request.META['wsgi.url_scheme'],
            http_host
        )
        self.api_url = "{}{}".format(self.base_url, request.path)
        self.api_url = self.api_url.rstrip("/")

        if ids is not None:
            self.api_url = self.api_url.rsplit("/", 1)[0]

        if resource_name is not None:
            self.api_url = self.api_url.rsplit("/", 1)[0]

    def map_view(self, request):
        """ Show information about available resources.

        .. versionadded:: 0.5.7
            Content-Type check

        :return django.http.HttpResponse

        """
        self.update_urls(request)
        resource_info = {
            "resources": [{
                "id": index + 1,
                "href": "{}/{}".format(self.api_url, resource_name),
            } for index, (resource_name, resource) in enumerate(
                sorted(self.resource_map.items()))
                if not resource.Meta.authenticators or
                resource.authenticate(request) is not None
            ]
        }
        response = json.dumps(resource_info)
        return HttpResponse(response, content_type="application/vnd.api+json")

    def handler_view_get(self, resource, **kwargs):
        items = json.dumps(
            resource.get(**kwargs),
            cls=resource.Meta.encoder
        )
        return HttpResponse(items, content_type=self.CONTENT_TYPE)

    def handler_view_post(self, resource, **kwargs):
        response = resource.post(**kwargs)
        return HttpResponse(
            response, content_type=self.CONTENT_TYPE, status=201)

    def handler_view_put(self, resource, **kwargs):
        response = resource.put(**kwargs)
        return HttpResponse(
            response, content_type=self.CONTENT_TYPE, status=200)

    def handler_view_delete(self, resource, **kwargs):
        if 'ids' not in kwargs:
            return HttpResponse("Resource ids not specified", status=404)

        response = resource.delete(**kwargs)
        return HttpResponse(
            response, content_type=self.CONTENT_TYPE, status=204)

    def handler_view(self, request, resource_name, ids=None):
        """ Handler for resources.

        .. versionadded:: 0.5.7
            Content-Type check

        :return django.http.HttpResponse

        """
        self.update_urls(request, resource_name=resource_name, ids=ids)
        resource = self.resource_map[resource_name]

        allowed_http_methods = {
            getattr(API.HTTP_METHODS, x) for x in resource.Meta.allowed_methods}
        if request.method not in allowed_http_methods:
            return HttpResponseNotAllowed(
                permitted_methods=allowed_http_methods)

        if resource.Meta.authenticators:
            user = resource.authenticate(request)
            if user is None or not user.is_authenticated():
                return HttpResponse("Not Authenticated", status=404)

        kwargs = dict(request=request)
        if ids is not None:
            kwargs['ids'] = ids.split(",")

        if request.method == "GET":
            return self.handler_view_get(resource, **kwargs)
        elif request.method == "POST":
            return self.handler_view_post(resource, **kwargs)
        elif request.method == "PUT":
            return self.handler_view_put(resource, **kwargs)
        elif request.method == "DELETE":
            return self.handler_view_delete(resource, **kwargs)
