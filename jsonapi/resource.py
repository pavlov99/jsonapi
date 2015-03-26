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
from django.core.paginator import Paginator
from django.db import models, transaction
from django.forms import ModelForm
import inspect
import json
import logging

from .utils import classproperty
from .django_utils import get_model_name, get_model_by_name
from .serializers import Serializer
from .auth import Authenticator
from .request_parser import RequestParser
from .model_inspector import ModelInspector
from .exceptions import JSONAPIError
from . import statuses

__all__ = 'Resource',

logger = logging.getLogger(__name__)


model_inspector = ModelInspector()
model_inspector.inspect()


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

            cls.Meta.model_info = model_inspector.models[cls.Meta.model]
            cls.Meta.default_form = cls.Meta.form or cls.get_form()

        cls.Meta.description = cls.__doc__ or ""
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
            queryset = cls.update_user_queryset(queryset, user, **kwargs)
        return queryset

    @classmethod
    def update_user_queryset(cls, queryset, user=None, **kwargs):
        """ Update queryset based on given user.

        .. versionadded:: 0.6.9

        Method is used to control permissions during resource management.

        """
        user_filter = models.Q()
        for path in cls.Meta.model_info.auth_user_paths:
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
        meta_attributes["fields"] = '__all__'

        if fields is not None:
            meta_attributes["fields"] = fields

        Form = type('Form', (ModelForm,), {
            "Meta": type('Meta', (object,), meta_attributes)
        })
        return Form

    @classmethod
    def _get_include_structure(cls, include=None):
        result = []
        include = include or []

        for include_path in include:
            current_model = cls.Meta.model
            field_path = []

            for include_name in include_path.split('.'):
                model_info = model_inspector.models[current_model]
                field = model_info.field_resource_map[include_name]
                field_path.append(field)
                current_model = field.related_model

            result.append({
                "field_path": field_path,
                "model_info": model_inspector.models[current_model],
                "resource": cls.Meta.api.model_resource_map[current_model],
                "type": field_path[-1].related_resource_name,
                "query": "__".join([f.query_name for f in field_path])
            })

        return result

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

        include = queryargs.get("include", [])
        include_structure = cls._get_include_structure(include)
        # TODO: update queryset based on include parameters.

        # Fields serialisation
        # NOTE: currently filter only own fields
        model_info = cls.Meta.model_info
        fields_own = model_info.fields_own
        if queryargs['fields']:
            fieldnames = queryargs['fields']
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

        response = cls.dump_documents(
            cls,
            objects,
            fields_own=fields_own,
            include_structure=include_structure
        )
        if meta:
            response["meta"] = meta
        return response

    @classmethod
    def post(cls, request=None, **kwargs):
        jdata = request.body.decode('utf8')
        data = json.loads(jdata)
        items = data["data"]
        is_collection = isinstance(items, list)

        if not is_collection:
            items = [items]

        forms = []
        for item in items:
            if 'links' in item:
                item.update(item.pop('links'))
            Form = cls.Meta.form or cls.get_form()
            form = Form(item)
            forms.append(form)

            if not form.is_valid():
                response = {
                    "errors": [{
                        "status": 400,
                        "title": "Validation error",
                        "data": form.errors
                    }]
                }
                return response

        data = []
        try:
            with transaction.atomic():
                for form in forms:
                    instance = form.save()
                    data.append(cls.dump_document(instance))
        except Exception as e:
            response = {
                "errors": [{
                    "status": 400,
                    "title": "Instance save error",
                    "data": {
                        "type": e.__class__.__name__,
                        "args": e.args,
                        "message": str(e)
                    }
                }]
            }
            return response

        if not is_collection:
            data = data[0]

        response = dict(data=data)
        return response

    @classmethod
    def put(cls, request=None, **kwargs):
        jdata = request.body.decode('utf8')
        data = json.loads(jdata)
        items = data["data"]
        is_collection = isinstance(items, list)

        if not is_collection:
            items = [items]

        ids_set = set([int(_id) for _id in kwargs['ids']])
        item_ids_set = {item["id"] for item in items}
        if ids_set != item_ids_set:
            msg = "ids set in url and request body are not matched"
            raise JSONAPIError(statuses.HTTP_400_BAD_REQUEST, msg)

        user = cls.authenticate(request)
        queryset = cls.get_queryset(user=user, **kwargs)
        queryset = cls.update_put_queryset(queryset, **kwargs)
        objects_map = queryset.in_bulk(kwargs["ids"])

        if len(objects_map) < len(kwargs["ids"]):
            msg = "You do not have access to objects {}".format(
                list(ids_set - set(objects_map.keys()))
            )
            raise JSONAPIError(statuses.HTTP_403_FORBIDDEN, msg)

        forms = []
        for item in items:
            if 'links' in item:
                item.update(item.pop('links'))
            Form = cls.Meta.form or cls.get_form(item.keys())
            instance = objects_map[item["id"]]
            form = Form(item, instance=instance)
            forms.append(form)

            if not form.is_valid():
                response = {
                    "errors": [{
                        "status": 400,
                        "title": "Validation error",
                        "data": form.errors
                    }]
                }
                return response

        data = []
        try:
            with transaction.atomic():
                for form in forms:
                    instance = form.save()
                    data.append(cls.dump_document(instance))
        except Exception as e:
            response = {
                "errors": [{
                    "status": 400,
                    "title": "Instance save error",
                    "data": {
                        "type": e.__class__.__name__,
                        "args": e.args,
                        "message": str(e)
                    }
                }]
            }
            return response

        if not is_collection:
            data = data[0]

        response = dict(data=data)
        return response

    @classmethod
    def delete(cls, request=None, **kwargs):
        user = cls.authenticate(request)
        queryset = cls.get_queryset(user=user, **kwargs)
        queryset.filter(id__in=kwargs['ids']).delete()
        return ""
