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
    def dump_document(cls, model, fields=None):
        """ Get document for model.

        :param django.db.models.Model model: model instance
        :param list of None fields: model field to dump
        :return dict: document

        """
        document = {
            "id": cls.get_id(model)
        }
        return document

    @classmethod
    def load_document(cls, model):
        pass

    @classmethod
    def get_id(cls, model):
        return model.pk
