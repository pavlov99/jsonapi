""" Deserializer definition."""


class DeserializerMeta(object):
    pass


class Deserializer(object):

    Meta = DeserializerMeta

    @classmethod
    def load_document(cls, document):
        """ Given document get model.

        :param dict document: Document
        :return django.db.models.Model model: model instance

        """
        pass
