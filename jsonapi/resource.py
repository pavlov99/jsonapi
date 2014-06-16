""" Resource definition."""
from . import six
import inspect
import logging
from django.db import models
from django.core.paginator import Paginator

from .utils import classproperty, Choices
from .serializers import Serializer

__all__ = 'Resource',

logger = logging.getLogger(__name__)


class ResourceManager(object):

    """ Resource utils functionality."""

    @staticmethod
    def get_resource_name(resource):
        """ Define resource name based on Meta information.

        :param Resource.Meta meta: resource metainformation
        :return: name of resource
        :rtype: str

        """
        name = getattr(resource.Meta, 'name', None)
        if name is not None:
            return name
        else:
            return ResourceManager.get_concrete_model(
                resource.Meta)._meta.model_name

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
            model = models.get_model(app_name, model_name)
        elif inspect.isclass(model) and issubclass(model, models.Model):
            pass
        else:
            raise ValueError("{0} is not a Django model".format(model))

        if model._meta.abstract:
            raise ValueError(
                "Abstract model {} could not be resource".format(model))

        return model


class ResourceMeta(type):

    """ Metaclass for JSON:API resources."""

    def __new__(mcs, name, bases, attrs):
        cls = super(ResourceMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.Meta.name = ResourceManager.get_resource_name(cls)
        cls.Meta.name_plural = "{0}s".format(cls.Meta.name)
        cls.Meta.model = ResourceManager.get_concrete_model(cls.Meta)
        cls.Meta.fieldnames_include = getattr(
            cls.Meta, 'fieldnames_include', None)
        cls.Meta.fieldnames_exclude = getattr(
            cls.Meta, 'fieldnames_exclude', None)
        cls.Meta.page_size = getattr(cls.Meta, 'page_size', None)
        return cls


@six.add_metaclass(ResourceMeta)
class Resource(Serializer):

    """ Base JSON:API resource class."""

    FIELD_TYPES = Choices(
        ('own', 'OWN'),
        ('to_one', 'TO_ONE'),
        ('to_many', 'TO_MANY'),
    )

    class Meta:
        name = ""

    @classmethod
    def _get_fields_own(cls, model):
        fields = {
            field.name: {
                "type": Resource.FIELD_TYPES.OWN,
                "name": field.name,
                "related_resource": None,
            } for field in model._meta.fields
            if field.rel is None and (field.serialize or field.name == 'id')
        }
        return fields

    @classmethod
    def _get_fields_self_foreign_key(cls, model):
        fields = {}
        model_resource_map = cls.Meta.api.model_resource_map
        for field in model._meta.fields:
            if field.rel and field.rel.multiple:
                # relationship is ForeignKey
                related_model = field.rel.to
                if related_model in model_resource_map:
                    # there is resource for related model
                    related_resource = model_resource_map[related_model]
                    fields[related_resource.Meta.name] = {
                        "type": Resource.FIELD_TYPES.TO_ONE,
                        "name": field.name,
                        "related_resource": related_resource,
                    }

        return fields

    @classmethod
    def _get_fields_others_foreign_key(cls, model):
        fields = {}
        model_resource_map = cls.Meta.api.model_resource_map
        for related_model, related_resource in model_resource_map.items():
            if related_model == model:
                # Do not check relationship with self
                continue

            for field in related_model._meta.fields:
                if field.rel and field.rel.to == model and field.rel.multiple:
                    # and not issubclass(related_model, model)? <- OneToOne rel
                    fields[related_resource.Meta.name_plural] = {
                        "type": Resource.FIELD_TYPES.TO_MANY,
                        "name": field.rel.related_name or "{}_set".format(
                            # get actual (parent) model
                            field.model._meta.model_name
                        ),
                        "related_resource": related_resource,
                    }
        return fields

    @classmethod
    def _get_fields_self_many_to_many(cls, model):
        fields = {}
        model_resource_map = cls.Meta.api.model_resource_map
        for field in model._meta.many_to_many:
            related_model = field.rel.to
            if related_model in model_resource_map:
                # there is resource for related model
                related_resource = model_resource_map[related_model]
                fields[related_resource.Meta.name_plural] = {
                    "type": Resource.FIELD_TYPES.TO_MANY,
                    "name": field.name,
                    "related_resource": related_resource,
                }
        return fields

    @classmethod
    def _get_fields_others_many_to_many(cls, model):
        fields = {}
        model_resource_map = cls.Meta.api.model_resource_map
        for related_model, related_resource in model_resource_map.items():
            if related_model == model:
                # Do not check relationship with self
                continue

            for field in related_model._meta.many_to_many:
                if field.rel.to == model:
                    fields[related_resource.Meta.name_plural] = {
                        "type": Resource.FIELD_TYPES.TO_MANY,
                        "name": field.rel.related_name or "{}_set".format(
                            # get actual (parent) model
                            field.model._meta.model_name
                        ),
                        "related_resource": related_resource,
                    }
        return fields

    @classproperty
    def fields(cls):
        """ Get resource fields.

        Analyze related to resource model and models related to it.
        Method builds resource relations based on related model relationship.
        If there is no resource for related model, corresponding field would
        not appear in resource, because there are no rules to serialize it.

        :return dict: fields with following format:
            {
                fieldname: {
                    "type": ["own"|"to_one"|"to_many"],
                    "related_resource": [None|<resource>],
                    "name": model field name: "title, author_id, comment_set"
                }
            }

        fieldname is given according to resource names, to follow jsonapi
        name attribute is name of Django model field.

        #1 Get fields from model own
        #2 Get fields from model foreign keys
        #3 Get foreign keys from other models to current
        #4 Get many-to-many fields from model
        #5 Get many-to-many from other models to current

        """
        model = getattr(cls.Meta, 'model', None)
        fields = {}
        if model is None:
            return fields

        fields.update(cls._get_fields_own(model))
        fields.update(cls._get_fields_self_foreign_key(model))
        fields.update(cls._get_fields_others_foreign_key(model))
        fields.update(cls._get_fields_self_many_to_many(model))
        fields.update(cls._get_fields_others_many_to_many(model))

        if cls.Meta.fieldnames_include is not None:
            for fieldname in cls.Meta.fieldnames_include:
                fields[fieldname] = {
                    "type": Resource.FIELD_TYPES.OWN,
                    "name": fieldname,
                    "related_resource": None,
                }

        fields = {
            k: v for k, v in fields.items()
            if cls.Meta.fieldnames_exclude is None or
            v["name"] not in cls.Meta.fieldnames_exclude
        }

        return fields

    @classproperty
    def fields_own(cls):
        return {
            k: v for k, v in cls.fields.items()
            if v["type"] == Resource.FIELD_TYPES.OWN
        }

    @classproperty
    def fields_to_one(cls):
        return {
            k: v for k, v in cls.fields.items()
            if v["type"] == Resource.FIELD_TYPES.TO_ONE
        }

    @classproperty
    def fields_to_many(cls):
        return {
            k: v for k, v in cls.fields.items()
            if v["type"] == Resource.FIELD_TYPES.TO_MANY
        }

    @classmethod
    def get(cls, **kwargs):
        """ Get resource http response.

        :return str: resource

        """
        model = cls.Meta.model
        filters = {}
        if kwargs.get('ids'):
            filters["id__in"] = kwargs.get('ids')

        queryset = model.objects.filter(**filters)
        objects = queryset
        meta = {}
        if cls.Meta.page_size is not None:
            paginator = Paginator(queryset, cls.Meta.page_size)
            page = int(kwargs.get('page', 1))
            meta["count"] = paginator.count
            meta["num_pages"] = paginator.num_pages
            meta["page_size"] = cls.Meta.page_size
            meta["page"] = page
            objects = paginator.page(page)

            meta["page_next"] = objects.next_page_number() \
                if objects.has_next() else None
            meta["page_prev"] = objects.previous_page_number() \
                if objects.has_previous() else None

        data = [
            cls.dump_document(
                m,
                fields=cls.fields_own,
                fields_to_one=cls.fields_to_one,
                #fields_to_many=cls.fields_to_many
            )
            for m in objects
        ]
        response = {
            cls.Meta.name_plural: data
        }
        if meta:
            response["meta"] = meta
        return response
