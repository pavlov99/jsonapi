from django.db import models
from django.contrib.auth import get_user_model
from .utils import Choices
from .django_utils import get_model_name, get_models


class ModelInfo(object):

    def __init__(self, name, fields_own=None, fields_to_one=None,
                 fields_to_many=None, auth_user_paths=None, is_user=None):
        self.name = name
        self.fields_own = fields_own or []
        self.fields_to_one = fields_to_one or []
        self.fields_to_many = fields_to_many or []
        self.auth_user_paths = auth_user_paths or []
        self.is_user = is_user

    @property
    def relation_fields(self):
        return self.fields_to_one + self.fields_to_many


class Field(object):

    """ Field information.

    is_bidirectional is True if related model has reference to current model as
    well.

    Example:
    A -@ B -> BChild

    A has reference to B, but not BChild, but both B and BChild have reference
    to A. A to B fields are bidirectional, BChild to A field is not
    bidirectional.

    """

    CATEGORIES = Choices(
        ('own', 'OWN'),
        ('to_one', 'TO_ONE'),
        ('to_many', 'TO_MANY'),
    )

    def __init__(self, name, category, related_model=None, django_field=None):
        self.name = name
        self.related_model = related_model
        self.category = category
        self.is_bidirectional = None
        self.django_field = django_field

    @property
    def query_name(self):
        """ Get field name used in queries."""
        return get_model_name(get_parent(self.related_model))

    @property
    def related_resource_name(self):
        name = self.query_name
        name += "s" if self.category == self.CATEGORIES.TO_MANY else ""
        return name

    def __repr__(self):
        suffix = "({})".format(get_model_name(self.related_model))\
            if self.related_model else ""
        return "<Field: {}{}>".format(self.name, suffix)

    def __hash__(self):
        return hash((self.name, self.related_model, self.category))

    def __eq__(self, other):
        return hash(self) == hash(other)


def get_parent(model):
    model_set = set(get_models())
    for parent in reversed(model.mro()):
        if parent in model_set:
            return parent


class ModelInspector(object):

    """ Inspect Django models."""

    def inspect(self):
        user_model = get_user_model()

        self.models = {
            model: ModelInfo(
                get_model_name(model),
                fields_own=self._get_fields_own(model),
                fields_to_one=self._get_fields_self_foreign_key(model),
                fields_to_many=self._get_fields_others_foreign_key(model) +
                self._get_fields_self_many_to_many(model) +
                self._get_fields_others_many_to_many(model),
                is_user=(model is user_model or issubclass(model, user_model))
            ) for model in get_models()
        }

        for model, model_info in self.models.items():
            if model_info.is_user:
                model_info.auth_user_paths = ['']
            else:
                self._update_auth_user_paths_model(model)

            model_info.field_resource_map = {
                f.related_resource_name: f
                for f in model_info.fields_to_one + model_info.fields_to_many
            }

    @classmethod
    def _filter_child_model_fields(cls, fields):
        """ Keep only related model fields.

        Example: Inherited models: A -> B -> C
        B has one-to-many relationship to BMany.
        after inspection BMany would have links to B and C. Keep only B. Parent
        model A could not be used (It would not be in fields)

        :param list fields: model fields.
        :return list fields: filtered fields.

        """
        indexes_to_remove = set([])
        for index1, field1 in enumerate(fields):
            for index2, field2 in enumerate(fields):
                if index1 < index2 and index1 not in indexes_to_remove and\
                        index2 not in indexes_to_remove:
                    if issubclass(field1.related_model, field2.related_model):
                        indexes_to_remove.add(index1)

                    if issubclass(field2.related_model, field1.related_model):
                        indexes_to_remove.add(index2)

        fields = [field for index, field in enumerate(fields)
                  if index not in indexes_to_remove]

        return fields

    @classmethod
    def _get_fields_own(cls, model):
        fields = [
            Field(
                name=field.name,
                related_model=None,
                django_field=field,
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
                django_field=field,
                category=Field.CATEGORIES.TO_ONE
            ) for field in model._meta.fields
            if field.rel and field.rel.multiple
        ]
        return fields

    @classmethod
    def _get_fields_others_foreign_key(cls, model):
        """ Get to-namy related field.

        If related model has children, link current model only to related.
        Child links make relationship complicated.

        """
        fields = [
            Field(
                name=field.rel.related_name or "{}_set".format(
                    get_model_name(related_model)),
                related_model=related_model,
                django_field=field,
                category=Field.CATEGORIES.TO_MANY
            ) for related_model in get_models()
            if not related_model._meta.proxy
            for field in related_model._meta.fields
            if field.rel and field.rel.to is model._meta.concrete_model and
            field.rel.multiple
        ]
        fields = cls._filter_child_model_fields(fields)
        return fields

    @classmethod
    def _get_fields_self_many_to_many(cls, model):
        fields = [
            Field(
                name=field.name,
                related_model=field.rel.to,
                django_field=field,
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
                django_field=field,
                category=Field.CATEGORIES.TO_MANY
            ) for related_model in get_models()
            if related_model is not model
            for field in related_model._meta.many_to_many
            if field.rel.to is model._meta.concrete_model
        ]
        fields = cls._filter_child_model_fields(fields)
        return fields

    def _update_auth_user_paths_model(self, model):
        # (field from previous model, related field of this model, model)
        paths = [[(None, None, model)]]

        while paths:
            current_paths = paths
            paths = []

            for current_path in current_paths:
                current_model = current_path[-1][-1]
                current_model_info = self.models[current_model]

                # NOTE: calculate used models links. Link is defined by model
                # and field used.
                used_links = set()
                for node1, node2 in zip(current_path[:-1], current_path[1:]):
                    used_links.add((node1[2], node1[1]))
                    used_links.add((node2[2], node2[1]))
                    used_links.add((node1[2], node2[0]))

                for field in current_model_info.relation_fields:
                    related_model = field.related_model
                    related_model_info = self.models[related_model]

                    for related_field in related_model_info.relation_fields:
                        related_related_model = related_field.related_model
                        if (related_related_model is current_model or
                            issubclass(current_model, related_related_model)) \
                            and (current_model, field) not in used_links \
                            and (related_model, related_field) not in \
                                used_links:

                            path = current_path + [
                                (field, related_field, related_model)]

                            if related_model_info.is_user:
                                self.models[model].auth_user_paths.append(
                                    "__".join([
                                        get_model_name(p[2]) for p in path[1:]
                                    ]))
                            else:
                                paths.append(path)
