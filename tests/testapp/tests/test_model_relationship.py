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

    def test_fields_own(self):
        AResource = self.api.register(self.resources['A'])
        self.assertIn("id", AResource.fields_own)
        self.assertIn("field_abstract", AResource.fields_own)
        self.assertIn("field_a", AResource.fields_own)

        for fieldname, data in AResource.fields_own.items():
            self.assertEqual(data["related_resource"], None)
            self.assertEqual(data["name"], fieldname)

    def test_fields_own_inheritance(self):
        BResource = self.api.register(self.resources['B'])
        self.assertIn("id", BResource.fields_own)
        self.assertIn("field_abstract", BResource.fields_own)
        self.assertIn("field_a", BResource.fields_own)
        self.assertIn("field_b", BResource.fields_own)

        for fieldname, data in BResource.fields_own.items():
            self.assertEqual(data["related_resource"], None)
            self.assertEqual(data["name"], fieldname)

    def test_fields_to_one(self):
        """ Check Foreign keys registered within current resource model."""
        # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        AResource = self.api.register(self.resources['A'])

        # Do not show fields to not registered resources
        self.assertFalse(AResource.fields_to_one)

        AAbstractOneResource = self.api.register(
            self.resources['AAbstractOne'])
        self.assertNotIn("aone", AResource.fields_to_one)
        self.assertIn("aabstractone", AResource.fields_to_one)

        AOneResource = self.api.register(self.resources['AOne'])
        self.assertIn("aone", AResource.fields_to_one)
        self.assertIn("aabstractone", AResource.fields_to_one)

        self.assertEqual(
            AResource.fields_to_one["aabstractone"]["name"], "a_abstract_one")
        self.assertEqual(
            AResource.fields_to_one["aone"]["name"], "a_one")

        self.assertEqual(
            AResource.fields_to_one["aabstractone"]["related_resource"],
            AAbstractOneResource
        )
        self.assertEqual(
            AResource.fields_to_one["aone"]["related_resource"],
            AOneResource
        )

    def test_fields_to_one_inheritance(self):
        """ Check Foreign keys registered within resource inherited model."""
        self.api.register(self.resources['A'])
        AAbstractOneResource = self.api.register(
            self.resources['AAbstractOne'])
        AOneResource = self.api.register(self.resources['AOne'])
        BResource = self.api.register(self.resources['B'])
        self.api.register(self.resources['BManyToMany'])

        self.assertIn("aone", BResource.fields_to_one)
        self.assertIn("aabstractone", BResource.fields_to_one)
        self.assertNotIn("bmanytomany", BResource.fields_to_one)

        self.assertEqual(
            BResource.fields_to_one["aabstractone"]["name"], "a_abstract_one")
        self.assertEqual(BResource.fields_to_one["aone"]["name"], "a_one")

        self.assertEqual(
            BResource.fields_to_one["aabstractone"]["related_resource"],
            AAbstractOneResource
        )
        self.assertEqual(
            BResource.fields_to_one["aone"]["related_resource"],
            AOneResource
        )

    def test_fields_to_many_other_model_foreign_key_default(self):
        AResource = self.api.register(self.resources['A'])
        AOneResource = self.api.register(self.resources['AOne'])
        self.assertIn("as", AOneResource.fields_to_many)
        self.assertEqual(AOneResource.fields_to_many["as"]["name"], "a_set")
        self.assertEqual(AOneResource.fields_to_many["as"]["related_resource"],
                         AResource)

    def test_fields_to_many_other_model_foreign_key_related_name(self):
        BResource = self.api.register(self.resources['B'])
        BManyResource = self.api.register(self.resources['BMany'])
        self.assertIn("bmanys", BResource.fields_to_many)
        self.assertEqual(BResource.fields_to_many["bmanys"]["name"], "bmanys")
        self.assertEqual(
            BResource.fields_to_many["bmanys"]["related_resource"],
            BManyResource)

    def test_fields_to_many_other_model_foreign_key_inheritance(self):
        """ Check foreign key related model of parent class.


        NOTE: relation schema is following:
                               AOne
                                 |
                                 @
            AAbstract ==> AA --> A --> B

        From B class there is relationship to AOne. Generate related field name
        using actual A class, not oldest parent AA.

        """
        AResource = self.api.register(self.resources['A'])
        self.api.register(self.resources['AA'])  # be sure, resource not skiped
        BResource = self.api.register(self.resources['B'])
        AOneResource = self.api.register(self.resources['AOne'])
        self.assertIn("bs", AOneResource.fields_to_many)
        self.assertEqual(AOneResource.fields_to_many["bs"]["name"], "a_set")
        self.assertEqual(AOneResource.fields_to_many["as"]["related_resource"],
                         AResource)
        self.assertEqual(AOneResource.fields_to_many["bs"]["related_resource"],
                         BResource)

    def test_fields_to_many_parent_child(self):
        # A does not have link to B: A.b_set
        # B does not have link to A: B.a
        AResource = self.api.register(self.resources['A'])
        BResource = self.api.register(self.resources['B'])

        for field, data in AResource.fields_to_many.items():
            self.assertNotEqual(data["name"], "b_set")
            self.assertNotEqual(data["related_resource"], BResource)

        for field, data in BResource.fields_to_one.items():
            self.assertNotEqual(data["name"], "a")
            self.assertNotEqual(data["related_resource"], AResource)

    def test_fields_to_many_many_to_many(self):
        # A -> AManyToMany, AAbstractManyToMany
        AResource = self.api.register(self.resources['A'])
        AManyToManyResource = self.api.register(self.resources['AManyToMany'])
        AAbstractManyToManyResource = self.api.register(
            self.resources['AAbstractManyToMany'])
        self.assertEqual(
            set(AResource.fields_to_many.keys()),
            {"amanytomanys", "aabstractmanytomanys"}
        )
        self.assertEqual(
            AResource.fields_to_many["amanytomanys"]["related_resource"],
            AManyToManyResource
        )
        self.assertEqual(
            AResource.fields_to_many["amanytomanys"]["name"],
            "a_many_to_manys"
        )
        self.assertEqual(
            AResource.fields_to_many["aabstractmanytomanys"][
                "related_resource"],
            AAbstractManyToManyResource
        )
        self.assertEqual(
            AResource.fields_to_many["aabstractmanytomanys"]["name"],
            "a_abstract_many_to_manys"
        )

    def test_fields_to_many_many_to_many_inheritance(self):
        # B -> AManyToMany, AAbstractManyToMany, BManyToMany (related_name)
        BResource = self.api.register(self.resources['B'])
        AManyToManyResource = self.api.register(self.resources['AManyToMany'])
        AAbstractManyToManyResource = self.api.register(
            self.resources['AAbstractManyToMany'])
        BManyToManyResource = self.api.register(self.resources['BManyToMany'])

        self.assertEqual(
            set(BResource.fields_to_many.keys()),
            {"amanytomanys", "aabstractmanytomanys", "bmanytomanys"}
        )
        self.assertEqual(
            BResource.fields_to_many["amanytomanys"]["related_resource"],
            AManyToManyResource
        )
        self.assertEqual(
            BResource.fields_to_many["amanytomanys"]["name"],
            "a_many_to_manys"
        )
        self.assertEqual(
            BResource.fields_to_many["aabstractmanytomanys"][
                "related_resource"],
            AAbstractManyToManyResource
        )
        self.assertEqual(
            BResource.fields_to_many["aabstractmanytomanys"]["name"],
            "a_abstract_many_to_manys"
        )
        self.assertEqual(
            BResource.fields_to_many["bmanytomanys"]["related_resource"],
            BManyToManyResource
        )
        self.assertEqual(
            BResource.fields_to_many["bmanytomanys"]["name"],
            "bmanytomanys"  # related name
        )

    def test_fields_to_many_other_model_many_to_many(self):
        # AManyToMany -> A
        AResource = self.api.register(self.resources['A'])
        AManyToManyResource = self.api.register(self.resources['AManyToMany'])
        self.assertEqual(
            set(AManyToManyResource.fields_to_many.keys()), {"as"})
        self.assertEqual(
            AManyToManyResource.fields_to_many["as"]["related_resource"],
            AResource)
        self.assertEqual(
            AManyToManyResource.fields_to_many["as"]["name"], "a_set")

    def test_fields_to_many_other_model_many_to_many_inheritance(self):
        """ Check foreign key related model of parent class.


        NOTE: relation schema is following:
                            AManyToMany
                                 @
                                 @
            AAbstract ==> AA --> A --> B

        """
        AResource = self.api.register(self.resources['A'])
        self.api.register(self.resources['AA'])  # be sure, resource not skiped
        BResource = self.api.register(self.resources['B'])
        AManyToManyResource = self.api.register(self.resources['AManyToMany'])

        self.assertIn("bs", AManyToManyResource.fields_to_many)
        self.assertEqual(
            AManyToManyResource.fields_to_many["bs"]["name"], "a_set")
        self.assertEqual(
            AManyToManyResource.fields_to_many["as"]["related_resource"],
            AResource)
        self.assertEqual(
            AManyToManyResource.fields_to_many["bs"]["related_resource"],
            BResource)
