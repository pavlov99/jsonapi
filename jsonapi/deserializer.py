""" Deserializer definition."""
from django.forms import ModelForm
import ast

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
    def load_documents(cls, input):
        """ Given document get model.

        :param str input: documents

        """
        data = ast.literal_eval(input)
        return data
