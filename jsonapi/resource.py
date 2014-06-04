""" Resource definition."""
from . import six


__all__ = 'Resource',


class ResourceManager(object):

    """ Resource utils functionality."""

    @staticmethod
    def get_resource_name(meta):
        """ Define resource name based on Meta information.

        :param Resource.Meta meta: resource metainformation

        """
        name = getattr(meta, 'name', None)
        if name is not None:
            return name
        else:
            # TODO: if model is not defined?
            return meta.model._meta.model_name


class ResourceMeta(type):

    def __new__(cls, name, bases, attrs):
        class_ = super(ResourceMeta, cls).__new__(cls, name, bases, attrs)
        class_.Meta.name = ResourceManager.get_resource_name(class_.Meta)
        return class_


@six.add_metaclass(ResourceMeta)
class Resource(object):
    class Meta:
        name = "_"

    def get(self):
        pass

    def create(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
