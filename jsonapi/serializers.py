""" Serializer definition."""


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

    """

    @classmethod
    def dump_document(cls, model_instance, fields=None, fields_to_one=None,
                      fields_to_many=None):
        """ Get document for model_instance.

        :param django.db.models.Model model_instance: model instance
        :param list of None fields: model_instance field to dump
        :return dict: document

        """
        fields = fields or []
        fields_to_one = fields_to_one or []
        fields_to_many = fields_to_many or []

        # apply rules for field serialization
        document = {
            f.name: getattr(model_instance, f.name)
            for f in cls.get_fields(model_instance.__class__)
            if f.rel is None
        }

        if fields_to_one or fields_to_many:
            document["links"] = {}

        # Own fields: f.rel = None
        # single table inheritance: f.rel != None and f.serialize = False
        # related fields: f.rel != None, f.serialize = True
        return document

    @classmethod
    def load_document(cls, document):
        """ Given document get model.

        :param dict document: Document
        :return django.db.models.Model model: model instance

        """

        pass

    @classmethod
    def get_id(cls, model_instance):
        """ Get id for given model_instance.

        :param django.db.models.Model model_instance: model instance
        :return id: model id (primary key)

        """
        return model_instance.pk

    @classmethod
    def get_fields(cls, model):
        """ Get fields for given model.

        :param django.db.models.Model model: model instance
        :return list fields: model fields

        """
        return model._meta.fields + model._meta.many_to_many
