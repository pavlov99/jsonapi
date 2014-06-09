""" Resource definition."""
from . import six
import inspect
from django.db import models

from .serializers import Serializer


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
            return ResourceManager.get_concrete_model(meta)._meta.model_name

    @staticmethod
    def get_concrete_model(meta):
        """ Get model defined in Meta.

        :param Resource.Meta meta: resource metainformation
        :return: model or None
        :rtype django.db.models.Model or None:
        :raise ValueError: model is not found

        """
        model = getattr(meta, 'model', None)

        if model is None:
            return None

        if isinstance(model, six.string_types) and len(model.split('.')) == 2:
            app_name, model_name = model.split('.')
            return models.get_model(app_name, model_name)
        elif inspect.isclass(model) and issubclass(model, models.Model):
            return model
        else:
            raise ValueError("{0} is not a Django model".format(model))

    @staticmethod
    def get_model_fields(model):
        """ Get fields for model.

        :return dict: fields

        """
        if model is None:
            return None

        return {}


class ResourceMeta(type):

    """ Metaclass for JSON:API resources."""

    def __new__(mcs, name, bases, attrs):
        cls = super(ResourceMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.Meta.name = ResourceManager.get_resource_name(cls.Meta)
        cls.Meta.name_plural = "{0}s".format(cls.Meta.name)
        cls.Meta.model = ResourceManager.get_concrete_model(cls.Meta)
        cls.Meta.fields = ResourceManager.get_model_fields(cls.Meta.model)
        return cls


@six.add_metaclass(ResourceMeta)
class Resource(object):

    """ Base JSON:API resource class."""

    class Meta:
        name = "_"

    @classmethod
    def get(cls, **kwargs):
        """ Get resource http response.

        :return str: resource

        """
        import json
        model = cls.Meta.model
        data = [Serializer.dump_document(m) for m in model.objects.all()]
        response = json.dumps({cls.Meta.name_plural: data})
        return response
