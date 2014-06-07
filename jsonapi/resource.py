""" Resource definition."""
from . import six


__all__ = 'Resource',


class ResourceManager(object):

    """ Resource utils functionality."""

    @staticmethod
    def get_resource_name(meta):
        """ Define resource name based on Meta information.

        :param Resource.Meta meta: resource metainformation
        :return: name of resource
        :rtype: str

        """
        name = getattr(meta, 'name', None)
        if name is not None:
            return name
        else:
            return meta.model._meta.model_name


class ResourceMeta(type):

    """ Metaclass for JSON:API resources."""

    def __new__(mcs, name, bases, attrs):
        cls = super(ResourceMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.Meta.name = ResourceManager.get_resource_name(cls.Meta)
        cls.Meta.name_plural = "{0}s".format(cls.Meta.name)
        return cls


@six.add_metaclass(ResourceMeta)
class Resource(object):

    """ Base JSON:API resource class."""

    class Meta:
        name = "_"

    @classmethod
    def get(cls, **kwargs):
        from django.core import serializers
        import json
        model = cls.Meta.model
        data = serializers.serialize("json", model.objects.all())
        response = json.dumps({cls.Meta.name_plural: json.loads(data)})
        return response
