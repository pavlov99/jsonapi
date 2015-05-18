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
    def dump_document(cls, instance, fields_own=None, fields_to_many=None):
        """ Get document for model_instance.

        redefine dump rule for field x: def dump_document_x

        :param django.db.models.Model instance: model instance
        :param list<Field> or None fields: model_instance field to dump
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
        if fields_own is not None:
            fields_own = {f.name for f in fields_own}
        else:
            fields_own = {
                f.name for f in instance._meta.fields
                if f.rel is None and f.serialize
            }
        fields_own.add('id')

        fields_own = (fields_own | set(cls.Meta.fieldnames_include))\
            - set(cls.Meta.fieldnames_exclude)

        document = {}
        # Include own fields
        for fieldname in fields_own:
            field_serializer = getattr(
                cls, "dump_document_{}".format(fieldname), None)

            if field_serializer is not None:
                value = field_serializer(instance)
            else:
                value = getattr(instance, fieldname)
                try:
                    field = instance._meta.get_field(fieldname)
                except models.fields.FieldDoesNotExist:
                    # Field is property, value already calculated
                    pass
                else:
                    if isinstance(field, models.fields.files.FileField):
                        # TODO: Serializer depends on API here.
                        value = cls.Meta.api.base_url + value.url
                    elif isinstance(field, models.CommaSeparatedIntegerField):
                        value = [v for v in value]

            document[fieldname] = value

        # Include to-one fields. It does not require database calls
        for field in instance._meta.fields:
            fieldname = "{}_id".format(field.name)
            # NOTE: check field is not related to parent model to exclude
            # <class>_ptr fields. OneToOne relationship field.rel.multiple =
            # False. Here make sure relationship is to parent model.
            if field.rel and not field.rel.multiple \
                    and isinstance(instance, field.rel.to):
                continue

            if field.rel and fieldname not in cls.Meta.fieldnames_exclude:
                document["links"] = document.get("links") or {}
                document["links"][field.name] = getattr(instance, fieldname)

        # Include to-many fields. It requires database calls. At this point we
        # assume that model was prefetch_related with child objects, which would
        # be included into 'linked' attribute. Here we need to add ids of linked
        # objects. To avoid database calls, iterate over objects manually and
        # get ids.
        fields_to_many = fields_to_many or []
        for field in fields_to_many:
            document["links"] = document.get("links") or {}
            document["links"][field.related_resource_name] = [
                obj.id for obj in getattr(instance, field.name).all()]

        return document

    @classmethod
    def dump_documents(cls, resource, model_instances, fields_own=None,
                       include_structure=None):
        model_instances = list(model_instances)
        model_info = resource.Meta.model_info
        include_structure = include_structure or []

        fields_to_many = set()
        for include_object in include_structure:
            f = include_object["field_path"][0]
            if f.category == f.CATEGORIES.TO_MANY:
                fields_to_many.add(f)

        data = {
            "data": [
                cls.dump_document(
                    m,
                    fields_own=fields_own,
                    fields_to_many=fields_to_many
                )
                for m in model_instances
            ]
        }

        # TODO: move links generation to other method.
        if model_info.fields_to_one or fields_to_many:
            data["links"] = {}
            for field in model_info.fields_to_one:
                linkname = "{}.{}".format(resource.Meta.name_plural, field.name)
                data["links"].update({
                    linkname: resource.Meta.api.api_url + "/" + field.name +
                    "/{" + linkname + "}"
                })

        if include_structure:
            data["linked"] = []

        for include_object in include_structure:
            current_models = set(model_instances)
            for field in include_object["field_path"]:
                related_models = set()
                for m in current_models:
                    if field.category == field.CATEGORIES.TO_MANY:
                        related_models |= set(getattr(m, field.name).all())
                    if field.category == field.CATEGORIES.TO_ONE:
                        related_model = getattr(m, field.name)
                        if related_model is not None:
                            related_models.add(related_model)

                current_models = related_models

            related_model_info = include_object["model_info"]
            related_resource = include_object["resource"]
            for rel_model in current_models:
                linked_obj = related_resource.dump_document(
                    rel_model, related_model_info.fields_own
                )
                linked_obj["type"] = include_object["type"]
                data["linked"].append(linked_obj)

        return data
