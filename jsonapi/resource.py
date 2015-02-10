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
    * allowed_methods = ('GET',)

Properties:

    * name_plural
    * is_model
    * is_inherited
    * is_auth_user

"""
from . import six
import ast
import inspect
import logging
import django
from django.core.paginator import Paginator
from django.forms import ModelForm
from django.db import models

from .utils import classproperty
from .django_utils import get_model_name, get_model_by_name
from .serializers import Serializer
from .auth import Authenticator
from .request_parser import RequestParser

__all__ = 'Resource',

logger = logging.getLogger(__name__)


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

    name = meta.name or get_model_name(get_concrete_model(meta.model))
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
        cls.Meta.name = get_resource_name(cls.Meta)

        if cls.Meta.is_model:
            model = get_concrete_model(cls.Meta.model)
            cls.Meta.model = model
            if model._meta.abstract:
                raise ValueError(
                    "Abstract model {} could not be resource".format(model))

        return cls


@six.add_metaclass(ResourceMetaClass)
class Resource(Serializer, Authenticator):

    """ Base JSON:API resource class."""

    class Meta:
        name = None
        # fieldnames_include = None  # NOTE: moved to Serializer.
        # fieldnames_exclude = None
        page_size = None
        allowed_methods = 'GET',
        form = None

        @classproperty
        def name_plural(cls):
            return "{0}s".format(cls.name)

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

        NOTE: use user from parameters, it could be authenticated not with
            session, so request.user might not work

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
    def update_get_queryset(cls, queryset, **kwargs):
        """ Update permission queryset for GET operations."""
        return queryset

    @classmethod
    def update_post_queryset(cls, queryset, **kwargs):
        """ Update permission queryset for POST operations."""
        return queryset

    @classmethod
    def update_put_queryset(cls, queryset, **kwargs):
        """ Update permission queryset for PUT operations."""
        return queryset

    @classmethod
    def update_delete_queryset(cls, queryset, **kwargs):
        """ Update permission queryset for delete operations."""
        return queryset

    @classmethod
    def get_form(cls, fields=None):
        """ Create Partial Form based on given fields.

        :param list fields: list of field names.

        """
        meta_attributes = {"model": cls.Meta.model}
        if django.VERSION[:2] >= (1, 6):
            meta_attributes["fields"] = '__all__'

        if fields is not None:
            meta_attributes["fields"] = fields

        Form = type('Form', (ModelForm,), {
            "Meta": type('Meta', (object,), meta_attributes)
        })
        return Form

    @classmethod
    def get(cls, request=None, **kwargs):
        """ Get resource http response.

        :return str: resource

        """
        user = cls.authenticate(request)
        queryset = cls.get_queryset(user=user, **kwargs)
        queryargs = RequestParser.parse(
            "&".join(["=".join(i) for i in request.GET.items()]))

        # Filters
        filters = queryargs.get("filters", {})
        if kwargs.get('ids'):
            filters["id__in"] = kwargs.get('ids')

        queryset = queryset.filter(**filters)

        # Sort
        if 'sort' in kwargs:
            queryset = queryset.order_by(*kwargs['sort'])

        # Fields serialisation
        # NOTE: currently filter only own fields
        model_info = cls.Meta.api.model_inspector.models[cls.Meta.model]
        fields_own = model_info.fields_own
        if queryargs['fields']:
            fieldnames = queryargs['fields']
            fieldnames.append("id")  # add id to fieldset
            fields_own = [f for f in fields_own if f.name in fieldnames]

        objects = queryset
        meta = {}
        if cls.Meta.page_size is not None:
            paginator = Paginator(queryset, cls.Meta.page_size)
            page = int(queryargs.get('page') or 1)
            meta["count"] = paginator.count
            meta["num_pages"] = paginator.num_pages
            meta["page_size"] = cls.Meta.page_size
            meta["page"] = page
            objects = paginator.page(page)

            meta["page_next"] = objects.next_page_number() \
                if objects.has_next() else None
            meta["page_prev"] = objects.previous_page_number() \
                if objects.has_previous() else None

        fields_include = set(queryargs.get("include", []))
        fields_to_one = [f for f in model_info.fields_to_one
                         if f.name in fields_include]
        fields_to_many = [f for f in model_info.fields_to_many
                          if f.name in fields_include]

        response = cls.dump_documents(
            cls,
            objects,
            fields_own=fields_own,
            fields_to_one=fields_to_one,
            fields_to_many=fields_to_many
        )
        if meta:
            response["meta"] = meta
        return response

    @classmethod
    def post(cls, request=None, **kwargs):
        jdata = request.body.decode('utf8')
        data = ast.literal_eval(jdata)
        items = data[cls.Meta.name_plural]
        is_collection = isinstance(items, list)

        if not is_collection:
            items = [items]

        objects = []
        Form = cls.Meta.form or cls.get_form()
        for item in items:
            form = Form(item)
            objects.append(form.save())

        data = [cls.dump_document(o) for o in objects]

        if not is_collection:
            data = data[0]

        response = {cls.Meta.name_plural: data}
        return response

    @classmethod
    def put(cls, request=None, **kwargs):
        # TODO: check ids for elements.
        # TODO: check form is valid for elements.
        # TODO: check kwargs has ids.
        jdata = request.body.decode('utf8')
        data = ast.literal_eval(jdata)
        items = data[cls.Meta.name_plural]
        is_collection = isinstance(items, list)

        if not is_collection:
            items = [items]

        objects_map = cls.Meta.model.objects.in_bulk(kwargs["ids"])

        objects = []
        Form = cls.Meta.form or cls.get_form()
        for item in items:
            instance = objects_map[item["id"]]
            form = Form(item, instance=instance)
            objects.append(form.save())

        data = [cls.dump_document(o) for o in objects]

        if not is_collection:
            data = data[0]

        response = {cls.Meta.name_plural: data}
        return response

    @classmethod
    def delete(cls, request=None, **kwargs):
        # TODO: raise Error if there are no ids.
        user = cls.authenticate(request)
        queryset = cls.get_queryset(user=user, **kwargs)
        queryset.filter(id__in=kwargs['ids']).delete()
        return ""
