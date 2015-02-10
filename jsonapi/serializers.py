""" Serializer definition."""
import json
import datetime
import decimal
from django.db import models


class DatetimeDecimalEncoder(json.JSONEncoder):

    """ Encoder for datetime and decimal serialization.

    Usage: json.dumps(object, cls=DatetimeDecimalEncoder)
    NOTE: _iterencode does not work

    """

    def default(self, o):
        """ Encode JSON.

        :return str: A JSON encoded string

        """
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()

        if isinstance(o, decimal.Decimal):
            return float(o)

        return json.JSONEncoder.default(self, o)


class SerializerMeta:
    encoder = DatetimeDecimalEncoder
    fieldnames_include = []
    fieldnames_exclude = []


class Serializer(object):

    """ Serializer class.

    Serializer has methods dump_document and load_document to convert model
    into document. Document is dictionary with following format:
        {
            "id"  // The document SHOULD contain an "id" key.
        }

    * The "id" key in a document represents a unique identifier for the
    underlying resource, scoped to its type. It MUST be a string which
    SHOULD only contain alphanumeric characters, dashes and underscores.

    In scenarios where uniquely identifying information between client and
    server is unnecessary (e.g., read-only, transient entities), JSON API
    allows for omitting the "id" key.

    Serializer:
        1) Check custom serializer for field in Resource
        2) Try to use predefined serializers for fields
        3) Try convert to string

    """

    Meta = SerializerMeta

    @classmethod
    def dump_document(cls, model_instance, fields_own=None, fields_to_one=None,
                      fields_to_many=None):
        """ Get document for model_instance.

        redefine dump rule for field x: def dump_document_x

        :param django.db.models.Model model_instance: model instance
        :param list<str> or None fields: model_instance field to dump
        :return dict: document

        Related documents are not included to current one. In case of to-many
        field serialization ensure that models_instance has been select_related
        so, no database calls would be executed.

        Method ensures that document has cls.Meta.fieldnames_include and does
        not have cls.Meta.fieldnames_exclude

        Steps:
        1) fieldnames_include could be properties, but not related models.
        Add them to fields_own.

        """
        default_fields_own = [
            f.name for f in model_instance._meta.fields if not f.rel]
        fields_own = fields_own or default_fields_own
        fields_own = (set(fields_own) | set(cls.Meta.fieldnames_include))\
            - set(cls.Meta.fieldnames_exclude)

        document = {}
        for fieldname in fields_own:
            value = getattr(model_instance, fieldname)
            field_serializer = getattr(
                cls, "dump_document_{}".format(fieldname), None)

            if field_serializer is not None:
                value = field_serializer(model_instance)
            else:
                try:
                    field = model_instance._meta.get_field(fieldname)
                except models.fields.FieldDoesNotExist:
                    # Field is property
                    value = getattr(model_instance, fieldname)
                else:
                    if isinstance(field, models.fields.files.FileField):
                        # TODO: Serializer depends on API here.
                        value = cls.Meta.api.base_url + value.url
                    elif isinstance(field, models.CommaSeparatedIntegerField):
                        value = [v for v in value]

            document[fieldname] = value

        fields_to_many = fields_to_many or []
        for field in model_instance._meta.fields:
            if field.rel:
                document["links"] = document.get("links") or {}
                document["links"][field.name] = getattr(
                    model_instance, "{}_id".format(field.name))

        for fieldname in fields_to_many:
            document["links"][fieldname] = list(
                getattr(model_instance, fieldname).
                values_list("id", flat=True)
            )

        return document

    @classmethod
    def dump_documents(cls, resource, model_instances, fields_own=None,
                       fields_to_one=None, fields_to_many=None):
        data = {
            resource.Meta.name_plural: [
                cls.dump_document(
                    m,
                    fields_own=[f.name for f in fields_own],
                    fields_to_one=[f.name for f in fields_to_one],
                    fields_to_many=[f.name for f in fields_to_many]
                )
                for m in model_instances
            ]
        }

        model_info = resource.Meta.api.model_inspector.models[
            resource.Meta.model]

        if model_info.fields_to_one or fields_to_many:
            data["links"] = {}
            for field in model_info.fields_to_one:
                linkname = "{}.{}".format(resource.Meta.name_plural, field.name)
                data["links"].update({
                    linkname: resource.Meta.api.api_url + "/" + field.name +
                    "/{" + linkname + "}"
                })

        fields_to_one = fields_to_one or []
        fields_to_many = fields_to_many or []

        if fields_to_one or fields_to_many:
            data["linked"] = {}

        for field in fields_to_one:
            related_model_info = resource.Meta.api.model_inspector.models[
                field.related_model]
            related_resource = cls.Meta.api.resource_map[
                related_model_info.name]
            data["linked"][related_resource.Meta.name_plural] = [
                related_resource.dump_document(
                    getattr(m, field.name),
                    [f.name for f in related_model_info.fields_own]
                ) for m in model_instances
                if getattr(m, field.name) is not None
            ]

        for field in fields_to_many:
            related_model_info = resource.Meta.api.model_inspector.models[
                field.related_model]
            related_resource = cls.Meta.api.resource_map[
                related_model_info.name]
            data["linked"][related_resource.Meta.name_plural] = [
                related_resource.dump_document(
                    x,
                    [f.name for f in related_model_info.fields_own]
                ) for m in model_instances
                for x in getattr(getattr(m, field.name), "all").__call__()
            ]

        return data
