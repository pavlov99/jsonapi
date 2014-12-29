from collections import namedtuple
from django.db import models
from .utils import Choices
from .django_utils import get_model_name, get_model_by_name


ModelInfo = namedtuple("ModelInfo", [
    "fields_own", "fields_to_one", "fields_to_many"
])


class Field(object):

    CATEGORIES = Choices(
        ('own', 'OWN'),
        ('to_one', 'TO_ONE'),
        ('to_many', 'TO_MANY'),
    )

    def __init__(self, name, category, related_model=None):
        self.name = name
        self.related_model = related_model
        self.category = category

    def query_name(self):
        """ Get field name used in queries."""
        return get_model_name(get_parent(self.related_model))

    def __repr__(self):
        suffix = "({})".format(get_model_name(self.related_model))\
            if self.related_model else ""
        return "<Field: {}{}>".format(self.name, suffix)

    def __hash__(self):
        return hash((self.name, self.related_model, self.category))

    def __eq__(self, other):
        return hash(self) == hash(other)


def get_parent(model):
    model_set = set(models.get_models())
    for parent in reversed(model.mro()):
        if parent in model_set:
            return parent


class ModelInspector(object):

    """ Inspect Django models."""

    def inspect(self):
        self.models = {
            model: ModelInfo(
                fields_own=self._get_fields_own(model),
                fields_to_one=self._get_fields_self_foreign_key(model),
                fields_to_many=self._get_fields_others_foreign_key(model) +\
                    self._get_fields_self_many_to_many(model) +\
                    self._get_fields_others_many_to_many(model)
        ) for model in models.get_models()}
        # auth_user_model = get_user_model()
        # user_info = [m for m in mi.models if m.model is auth_user_model][0]

    @classmethod
    def _get_fields_own(cls, model):
        fields = [
            Field(
                name=field.name,
                related_model=None,
                category=Field.CATEGORIES.OWN
            ) for field in model._meta.fields
            if field.rel is None and (field.serialize or field.name == 'id')
        ]
        return fields

    @classmethod
    def _get_fields_self_foreign_key(cls, model):
        fields = [
            Field(
                name=field.name,
                related_model=field.rel.to,
                category=Field.CATEGORIES.TO_ONE
            ) for field in model._meta.fields
            if field.rel and field.rel.multiple
        ]
        return fields

    @classmethod
    def _get_fields_others_foreign_key(cls, model):
        """ Get to-namy related field.

        If related model has children, link current model only to related. Child
        links make relationship complicated.

        """
        fields = [
            Field(
                name=field.rel.related_name or "{}_set".format(
                    get_model_name(related_model)),
                related_model=related_model,
                category=Field.CATEGORIES.TO_MANY
            ) for related_model in models.get_models()
            for field in related_model._meta.fields
            if related_model is not model and field.rel
            and field.rel.to is model and field.rel.multiple
            and related_model is get_parent(related_model)
        ]
        return fields

    @classmethod
    def _get_fields_self_many_to_many(cls, model):
        fields = [
            Field(
                name=field.name,
                related_model=field.rel.to,
                category=Field.CATEGORIES.TO_MANY
            ) for field in model._meta.many_to_many
        ]
        return fields

    @classmethod
    def _get_fields_others_many_to_many(cls, model):
        fields = [
            Field(
                name=field.rel.related_name or "{}_set".format(
                    get_model_name(related_model)),
                related_model=related_model,
                category=Field.CATEGORIES.TO_MANY
            ) for related_model in models.get_models()
            if related_model is not model
            for field in related_model._meta.many_to_many
            if field.rel.to is model
        ]
        return fields
