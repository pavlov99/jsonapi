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
from .django_utils import get_model_name
from .serializers import Serializer
from .deserializer import Deserializer
from .auth import Authenticator

__all__ = 'Resource',

logger = logging.getLogger(__name__)


class ResourceManager(object):

    """ Resource utils functionality."""

    @staticmethod
    def get_concrete_model_by_name(model_name):
        """ Get model by its name.

        :param str model_name: name of model.
        :return django.db.models.Model:

        Example:
            get_concrete_model_by_name('auth.User')
            django.contrib.auth.models.User

        """
        if isinstance(model_name, six.string_types) and \
                len(model_name.split('.')) == 2:
            app_name, model_name = model_name.split('.')
            model = models.get_model(app_name, model_name)
        else:
            raise ValueError("{0} is not a Django model".format(model_name))

        return model

    @staticmethod
    def get_concrete_model(model):
        """ Get model defined in Meta.

        :param str or django.db.models.Model model:
        :return: model or None
        :rtype django.db.models.Model or None:
        :raise ValueError: model is not found or abstract

        """
        if not(inspect.isclass(model) and issubclass(model, models.Model)):
            model = ResourceManager.get_concrete_model_by_name(model)

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

        name = meta.name or get_model_name(ResourceManager.get_concrete_model(meta.model))
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

    class Meta:
        name = None
        fieldnames_include = None
        fieldnames_exclude = None
        page_size = None
        allowed_methods = 'get',

        @classproperty
        def name_plural(cls):
            return "{0}s".format(cls.name)

        @classproperty
        def is_auth_user(cls):
            auth_user_model = ResourceManager.get_concrete_model_by_name(
                settings.AUTH_USER_MODEL)
            return cls.model is auth_user_model

        @classproperty
        def is_inherited(cls):
            is_base = (cls.model.mro()[1] is models.Model) or cls.is_auth_user
            return not is_base

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
    def __generate_user_resource_paths(cls, paths):
        if all(p[-1].Meta.is_auth_user for p in paths):
            return paths

        next_paths = []
        for path in paths:
            if path[-1].Meta.is_auth_user:
                next_paths.append(path)
            else:
                for field_info in path[-1].fields.values():
                    next_resource = field_info["related_resource"]
                    if next_resource is not None and next_resource not in path \
                            and not next_resource.Meta.is_inherited:
                        next_paths.append(path + [next_resource])
        return cls.__generate_user_resource_paths(next_paths)


    @classproperty
    def _auth_user_resource_paths(cls):
        """ Return information about AUTH_USER relation.

        :return Nont: for AUTH_USER resource
        :return list paths: List of paths to user resource.
            Each path is a list of visited resources.

        """
        if cls.Meta.is_auth_user:
            return None

        paths = cls.__generate_user_resource_paths([[cls]])
        # NOTE: current model is not included into query, so first element of
        # path is not included.
        result = [
            "__".join([
                get_model_name(resource.Meta.model) for resource in path[1:]
            ]) for path in paths
        ]
        return result

    @classmethod
    def get(cls, request=None, **kwargs):
        """ Get resource http response.

        :return str: resource

        """
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
                    user_filter = user_filter | Q(**{path: user})

                queryset = queryset.filter(user_filter)

        queryset = queryset.filter(**filters)
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
        model = cls.Meta.model
        items = data[cls.Meta.name_plural]

        model.objects.bulk_create([
            model(**item) for item in items
        ])
