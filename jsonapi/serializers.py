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
    def dump_document(cls, model_instance, fields=None, fields_to_one=None,
                      fields_to_many=None):
        """ Get document for model_instance.

        redefine dump rule for field x: def dump_document_x

        :param django.db.models.Model model_instance: model instance
        :param list of None fields: model_instance field to dump
        :return dict: document

        """
        fields = fields or {}
        fields_to_one = fields_to_one or {}
        fields_to_many = fields_to_many or {}

        document = {}
        # apply rules for field serialization
        for name, data in fields.items():
            value = getattr(model_instance, data["name"])

            field_serializer = getattr(
                cls, "dump_document_{}".format(data["name"]), None)

            if field_serializer is not None:
                value = field_serializer(value)
            else:
                try:
                    field = model_instance._meta.get_field(data["name"])
                except models.fields.FieldDoesNotExist:
                    # Field is property
                    pass
                else:
                    if isinstance(field, models.fields.files.FileField):
                        value = cls.Meta.api.base_url + value.url
                    elif isinstance(field, models.CommaSeparatedIntegerField):
                        value = [v for v in value]

            document[name] = value

        if fields_to_one or fields_to_many:
            document["links"] = {}

        for name, data in fields_to_one.items():
            document["links"][name] = getattr(
                model_instance, "{}_id".format(data["name"]))

        for name, data in fields_to_many.items():
            document["links"][name] = list(
                getattr(model_instance, data["name"]).
                values_list("id", flat=True)
            )

        return document

    @classmethod
    def load_document(cls, document):
        """ Given document get model.

        :param dict document: Document
        :return django.db.models.Model model: model instance

        """

        pass
