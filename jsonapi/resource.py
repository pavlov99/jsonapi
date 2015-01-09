""" Resource definition.

There are two tipes of resources:
    * simple resources
    * model resources

Simple resources require name Meta property to be defined.
Example:
    class SimpleResource(Resource):
        class Meta:
            name = "simple_name"

Django model resources require model to be defined
Example:
    class ModelResource(Resource):
        class Meta:
            model = "myapp.mymodel"

There are several optional Meta parameters:
    * fieldnames_include = None
    * fieldnames_exclude = None
    * page_size = None
    * allowed_methods = ('get',)

Properties:

    * name_plural
    * is_model
    * is_inherited
    * is_auth_user

"""
from . import six
import inspect
import logging
from django.conf import settings
from django.core.paginator import Paginator
from django.db import models

from .utils import classproperty, Choices
from .django_utils import get_model_name, get_model_by_name
from .serializers import Serializer
from .deserializer import Deserializer
from .auth import Authenticator

__all__ = 'Resource',

logger = logging.getLogger(__name__)


class ResourceManager(object):

    """ Resource utils functionality."""

    @staticmethod
    def get_concrete_model(model):
        """ Get model defined in Meta.

        :param str or django.db.models.Model model:
        :return: model or None
        :rtype django.db.models.Model or None:
        :raise ValueError: model is not found or abstract

        """
        if not(inspect.isclass(model) and issubclass(model, models.Model)):
            model = get_model_by_name(model)

        return model

    @staticmethod
    def get_resource_name(meta):
        """ Define resource name based on Meta information.

        :param Resource.Meta meta: resource meta information
        :return: name of resource
        :rtype: str
        :raises ValueError:

        """
        if meta.name is None and not meta.is_model:
            msg = "Either name or model for resource.Meta shoud be provided"
            raise ValueError(msg)

        name = meta.name or get_model_name(
            ResourceManager.get_concrete_model(meta.model))
        return name


def merge_metas(*metas):
    """ Merge meta parameters.

    next meta has priority over current, it will overwrite attributes.

    :param class or None meta: class with properties.
    :return class: merged meta.

    """
    metadict = {}
    for meta in metas:
        metadict.update(meta.__dict__)

    metadict = {k: v for k, v in metadict.items() if not k.startswith('__')}
    return type('Meta', (object, ), metadict)


class ResourceMetaClass(type):

    """ Metaclass for JSON:API resources.

    .. versionadded:: 0.5.0

    Meta.is_auth_user whether model is AUTH_USER or not
    Meta.is_inherited whether model has parent or not.

    Meta.is_model: whether resource based on model or not

    NOTE: is_inherited is used for related fields queries. For fields it is only
    parent model used (django.db.models.Model).

    """

    def __new__(mcs, name, bases, attrs):
        cls = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)
        metas = [getattr(base, 'Meta', None) for base in bases]
        metas.append(cls.Meta)
        cls.Meta = merge_metas(*metas)

        # NOTE: Resource.Meta should be defined before metaclass returns
        # Resource.
        if name == "Resource":
            return cls

        cls.Meta.is_model = bool(getattr(cls.Meta, 'model', False))
        cls.Meta.name = ResourceManager.get_resource_name(cls.Meta)

        if cls.Meta.is_model:
            model = ResourceManager.get_concrete_model(cls.Meta.model)
            cls.Meta.model = model
            if model._meta.abstract:
                raise ValueError(
                    "Abstract model {} could not be resource".format(model))

        return cls


@six.add_metaclass(ResourceMetaClass)
class Resource(Serializer, Deserializer, Authenticator):

    """ Base JSON:API resource class."""

    FIELD_TYPES = Choices(
        ('own', 'OWN'),
        ('to_one', 'TO_ONE'),
        ('to_many', 'TO_MANY'),
    )
    RESERVED_GET_PARAMS = ('include', 'sort', 'fields', 'page', 'ids')

    class Meta:
        name = None
        fieldnames_include = None
        fieldnames_exclude = None
        page_size = None
        allowed_methods = 'get',

        @classproperty
        def name_plural(cls):
            return "{0}s".format(cls.name)


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
                            get_model_name(field.model)
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
                            get_model_name(field.model)
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
    def get_queryset(cls, user=None, **kwargs):
        """ Get objects queryset.

        Method is used to generate objects queryset for resource operations.
        It is aimed to:
            * Filter objects based on user. Object could be in queryset only if
            there is attribute-ForeignKey-ManyToMany path from current resource
            to current auth_user.
            * Select related objects (or prefetch them) based on requested
            requested objects to include

        NOTE: if you need to get user in this method, use
        cls.authenticate(request), because user could be authenticated using
        HTTP_BASIC method, not only session.

        """
        queryset = cls.Meta.model.objects

        if cls.Meta.authenticators:
            model_info = cls.Meta.api.model_inspector.models[cls.Meta.model]
            user_filter = models.Q()
            for path in model_info.auth_user_paths:
                querydict = {path: user} if path else {"id": user.id}
                user_filter = user_filter | models.Q(**querydict)

            queryset = queryset.filter(user_filter)

        return queryset

    @classmethod
    def get(cls, request=None, **kwargs):
        """ Get resource http response.

        :return str: resource

        """
        user = cls.authenticate(request)
        queryset = cls.get_queryset(user=user, **kwargs)

        filters = {
            k: v for k, v in kwargs.items()
            if k not in cls.RESERVED_GET_PARAMS
            # k in cls.fields_own
        }
        if kwargs.get('ids'):
            filters["id__in"] = kwargs.get('ids')

        queryset = queryset.filter(**filters)

        # Sort
        if 'sort' in kwargs:
            queryset = queryset.order_by(*kwargs['sort'].split(","))

        # Fields serialisation
        fields = cls.fields_own
        if 'fields' in kwargs:
            fieldnames = kwargs['fields'].split(",")
            fieldnames.append("id")  # add id to fieldset
            fields = {
                name: value for name, value in fields.items()
                if name in fieldnames
            }

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
                fields=fields,
                fields_to_one=cls.fields_to_one,
                # fields_to_many=cls.fields_to_many
            )
            for m in objects
        ]
        response = {
            cls.Meta.name_plural: data
        }
        if meta:
            response["meta"] = meta
        return response

    @classmethod
    def create(cls, documents, request=None, **kwargs):
        data = cls.load_documents(documents)
        items = data[cls.Meta.name_plural]

        models = []
        for item in items:
            form = cls.Meta.form(item)
            models.append(form.save())

        return models

    @classmethod
    def delete(cls, request=None, **kwargs):
        model = cls.Meta.model
        queryset = model.objects

        filters = {}
        if kwargs.get('ids'):
            filters["id__in"] = kwargs.get('ids')

        if cls.Meta.authenticators:
            user = cls.authenticate(request)
            auth_user_resource_paths = cls._auth_user_resource_paths
            if auth_user_resource_paths is None:
                queryset = queryset.filter(id=user.id)
            else:
                user_filter = models.Q()
                for path in auth_user_resource_paths:
                    user_filter = user_filter | models.Q(**{path: user})

                queryset = queryset.filter(user_filter)

        queryset.filter(**filters).delete()
        return ""
