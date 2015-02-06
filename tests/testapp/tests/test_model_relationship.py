from django.test import TestCase
from django.contrib.auth import get_user_model
from jsonapi.api import API
from jsonapi.resource import Resource
from jsonapi.model_inspector import ModelInspector, Field

from ..models import (
    AAbstractOne, AAbstractManyToMany, AAbstract, AA, AOne, AManyToMany,
    A, B, BMany, BManyToMany, BProxy, Post, BManyToManyChild
)


class TestResourceRelationship(TestCase):
    def setUp(self):
        self.api = API()
        self.classes = dict(
            AAbstractOne=AAbstractOne,
            AAbstractManyToMany=AAbstractManyToMany,
            AAbstract=AAbstract,
            AA=AA,
            AOne=AOne,
            AManyToMany=AManyToMany,
            A=A,
            B=B,
            BMany=BMany,
            BManyToMany=BManyToMany,
            BManyToManyChild=BManyToManyChild,
            BProxy=BProxy,
            User=get_user_model(),
        )

        self.resources = {
            classname: type(
                '{}Resource'.format(classname),
                (Resource, ),
                {"Meta": type('Meta', (object,), {"model": cls})}
            ) for classname, cls in self.classes.items()
            if not cls._meta.abstract
        }
        self.model_inspector = ModelInspector()
        self.model_inspector.inspect()

    def test_model_User(self):
        model_info = self.model_inspector.models[self.classes["User"]]
        self.assertEqual(model_info.fields_to_one, [])
        field_names = [f.name for f in model_info.fields_to_many]
        self.assertEqual(len(field_names), len(set(field_names)))

        expected_fields = {
            Field("post_set", Field.CATEGORIES.TO_MANY, Post),
            Field("aa_set", Field.CATEGORIES.TO_MANY, self.classes["AA"]),
        }
        self.assertEqual(len(model_info.fields_to_many), 5)
        self.assertTrue(set(model_info.fields_to_many) > set(expected_fields))
        expected_auth_user_paths = [""]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_aabstract(self):
        self.assertFalse(
            self.classes["AAbstract"] in self.model_inspector.models)

    def test_model_aabstractone(self):
        model_info = self.model_inspector.models[self.classes["AAbstractOne"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_many = {
            Field("aa_set", Field.CATEGORIES.TO_MANY, self.classes["AA"]),
        }
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(model_info.fields_to_one, [])
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)

        expected_auth_user_paths = ["aa__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_aabstractmanytomany(self):
        model_info = self.model_inspector.models[
            self.classes["AAbstractManyToMany"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_many = {
            Field("testapp_aa_related", Field.CATEGORIES.TO_MANY,
                  self.classes["AA"]),
        }
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(model_info.fields_to_one, [])
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)

        expected_auth_user_paths = ["aa__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_aa(self):
        model_info = self.model_inspector.models[self.classes["AA"]]

        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field_abstract", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_one = {
            Field("user", Field.CATEGORIES.TO_ONE, self.classes["User"]),
            Field("a_abstract_one", Field.CATEGORIES.TO_ONE,
                  self.classes["AAbstractOne"]),
        }
        expected_fields_to_many = {
            Field("a_abstract_many_to_manys", Field.CATEGORIES.TO_MANY,
                  self.classes["AAbstractManyToMany"]),
        }
        self.assertEqual(set(model_info.fields_own), set(expected_fields_own))
        self.assertEqual(
            set(model_info.fields_to_one), set(expected_fields_to_one))
        self.assertEqual(
            set(model_info.fields_to_many), set(expected_fields_to_many))

        expected_auth_user_paths = ["user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_a(self):
        model_info = self.model_inspector.models[self.classes["A"]]

        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field_abstract", Field.CATEGORIES.OWN, None),
            Field("field_a", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_one = {
            Field("user", Field.CATEGORIES.TO_ONE, self.classes["User"]),
            Field("a_abstract_one", Field.CATEGORIES.TO_ONE,
                  self.classes["AAbstractOne"]),
            Field("a_one", Field.CATEGORIES.TO_ONE,
                  self.classes["AOne"]),
        }
        expected_fields_to_many = {
            Field("a_abstract_many_to_manys", Field.CATEGORIES.TO_MANY,
                  self.classes["AAbstractManyToMany"]),
            Field("a_many_to_manys", Field.CATEGORIES.TO_MANY,
                  self.classes["AManyToMany"]),
        }
        self.assertEqual(set(model_info.fields_own), set(expected_fields_own))
        self.assertEqual(
            set(model_info.fields_to_one), set(expected_fields_to_one))
        self.assertEqual(
            set(model_info.fields_to_many), set(expected_fields_to_many))

        expected_auth_user_paths = ["user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_aone(self):
        model_info = self.model_inspector.models[self.classes["AOne"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_many = {
            Field("a_set", Field.CATEGORIES.TO_MANY, self.classes["A"]),
        }
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(model_info.fields_to_one, [])
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)

        expected_auth_user_paths = ["a__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_amanytomany(self):
        model_info = self.model_inspector.models[self.classes["AManyToMany"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_many = {
            Field("a_set", Field.CATEGORIES.TO_MANY, self.classes["A"]),
        }
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(model_info.fields_to_one, [])
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)

        expected_auth_user_paths = ["a__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_b(self):
        model_info = self.model_inspector.models[self.classes["B"]]
        proxy_model_info = self.model_inspector.models[self.classes["BProxy"]]

        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field_abstract", Field.CATEGORIES.OWN, None),
            Field("field_a", Field.CATEGORIES.OWN, None),
            Field("field_b", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_one = {
            Field("user", Field.CATEGORIES.TO_ONE, self.classes["User"]),
            Field("a_abstract_one", Field.CATEGORIES.TO_ONE,
                  self.classes["AAbstractOne"]),
            Field("a_one", Field.CATEGORIES.TO_ONE,
                  self.classes["AOne"]),
        }
        expected_fields_to_many = {
            Field("a_abstract_many_to_manys", Field.CATEGORIES.TO_MANY,
                  self.classes["AAbstractManyToMany"]),
            Field("a_many_to_manys", Field.CATEGORIES.TO_MANY,
                  self.classes["AManyToMany"]),
            Field("bmanys", Field.CATEGORIES.TO_MANY,
                  self.classes["BMany"]),
            Field("bmanytomanys", Field.CATEGORIES.TO_MANY,
                  self.classes["BManyToMany"]),
        }
        self.assertEqual(set(model_info.fields_own), set(expected_fields_own))
        self.assertEqual(
            set(model_info.fields_to_one), set(expected_fields_to_one))
        self.assertEqual(
            set(model_info.fields_to_many), set(expected_fields_to_many))

        self.assertEqual(
            set(proxy_model_info.fields_own), set(expected_fields_own))
        self.assertEqual(
            set(proxy_model_info.fields_to_one), set(expected_fields_to_one))
        self.assertEqual(
            set(proxy_model_info.fields_to_many), set(expected_fields_to_many))

        expected_auth_user_paths = ["user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)
        self.assertEqual(
            proxy_model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_bmany(self):
        model_info = self.model_inspector.models[self.classes["BMany"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_one = {
            Field("b", Field.CATEGORIES.TO_ONE, self.classes["B"]),
        }
        expected_fields_to_many = set({})
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(set(model_info.fields_to_one), expected_fields_to_one)
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)
        expected_auth_user_paths = ["b__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_bmanytomany(self):
        model_info = self.model_inspector.models[self.classes["BManyToMany"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_one = set({})
        expected_fields_to_many = {
            Field("bs", Field.CATEGORIES.TO_MANY, self.classes["B"]),
        }
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(set(model_info.fields_to_one), expected_fields_to_one)
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)
        expected_auth_user_paths = ["b__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_model_bmanytomanychild(self):
        model_info = self.model_inspector.models[
            self.classes["BManyToManyChild"]]
        expected_fields_own = {
            Field("id", Field.CATEGORIES.OWN, None),
            Field("field", Field.CATEGORIES.OWN, None),
        }
        expected_fields_to_one = set({})
        expected_fields_to_many = {
            Field("bs", Field.CATEGORIES.TO_MANY, self.classes["B"]),
        }
        self.assertEqual(set(model_info.fields_own), expected_fields_own)
        self.assertEqual(set(model_info.fields_to_one), expected_fields_to_one)
        self.assertEqual(set(model_info.fields_to_many),
                         expected_fields_to_many)
        expected_auth_user_paths = ["b__user"]
        self.assertEqual(model_info.auth_user_paths, expected_auth_user_paths)

    def test_abstract_model_resource(self):
        with self.assertRaises(ValueError):
            class AAbstractResource(Resource):
                class Meta:
                    model = self.classes['AAbstract']
