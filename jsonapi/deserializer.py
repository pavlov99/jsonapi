""" Deserializer definition."""
from django.forms import ModelForm
from .utils import classproperty


class DeserializerMeta(object):

    @classproperty
    def form(cls):
        if cls.model is not None:
            class Form(ModelForm):
                class Meta:
                    model = cls.model
            return Form()
        else:
            return None


class Deserializer(object):

    Meta = DeserializerMeta

    @classmethod
    def load_document(cls, document):
        """ Given document get model.

        :param dict document: Document
        :return django.db.models.Model model: model instance

        """
        pass
