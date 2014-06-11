from django.test import TestCase, Client
import unittest
import json

from django.db import models
from mixer.backend.django import mixer

from jsonapi.resource import Resource
from jsonapi.api import API
from tests.testapp.resources import (
    AuthorResource,
    PostWithPictureResource,
)


class TestResourceRelationship(TestCase):
    def setUp(self):
        """ Setup classes with different relationship types.

        B is inherited from A
        All of the relationship for A class are defined in A
        All of the relationship for B class are defined in related classes

        There is no OneToMany relationship in Django, so there are no AMany
        and BOne classes.

            AAbstractOne      AOne  BManyToMany
                 |              |        @
                 |              |        |
                 @              @        @
             AAbstract =======> A -----> B ------ BProxy
                 @              @        |
                 |              |        |
                 @              @        @
        AAbstractManyToMany AManyToMany BMany

        """
        self.api = API()

        class AAbstractOne(models.Model):
            field = models.IntegerField()

        class AAbstractManyToMany(models.Model):
            field = models.IntegerField()

        class AAbstract(models.Model):
            class Meta:
                abstract = True

            field_abstract = models.IntegerField()
            a_abstract_one = models.ForeignKey(AAbstractOne)
            a_abstract_many_to_manys = models.ManyToManyField(
                AAbstractManyToMany,
                related_name="%(app_label)s_%(class)s_related"
            )

        class AOne(models.Model):
            field = models.IntegerField()

        class AManyToMany(models.Model):
            field = models.IntegerField()

        class A(AAbstract):
            field_a = models.IntegerField()
            a_one = models.ForeignKey(AOne)
            a_many_to_manys = models.ManyToManyField(AManyToMany)

        class B(A):
            field_b = models.IntegerField()

        class BMany(models.Model):
            field = models.IntegerField()
            b = models.ForeignKey(B, related_name="bmanys")

        class BManyToMany(models.Model):
            field = models.IntegerField()
            bs = models.ManyToManyField(B)

        class BProxy(B):
            class Meta:
                proxy = True

        self.classes = dict(
            AAbstractOne=AAbstractOne,
            AAbstractManyToMany=AAbstractManyToMany,
            AAbstract=AAbstract,
            AOne=AOne,
            AManyToMany=AManyToMany,
            A=A,
            B=B,
            BMany=BMany,
            BManyToMany=BManyToMany,
            BProxy=BProxy,
        )

        self.resources = {
            classname: type(
                '{}Resource'.format(classname),
                (Resource, ),
                {"Meta": type('Meta', (object,), {"model": cls})}
            ) for classname, cls in self.classes.items()
            if not cls._meta.abstract
        }

    def tearDown(self):
        del models.loading.cache.app_models['tests']

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

    def test_fields_to_one_other_model_foreign_key_default(self):
        AResource = self.api.register(self.resources['A'])
        AOneResource = self.api.register(self.resources['AOne'])
        self.assertIn("as", AOneResource.fields_to_many)
        self.assertEqual(AOneResource.fields_to_many["as"]["name"], "a_set")
        self.assertEqual(AOneResource.fields_to_many["as"]["related_resource"],
                         AResource)

    def test_fields_to_one_other_model_foreign_key_related_name(self):
        BResource = self.api.register(self.resources['B'])
        BManyResource = self.api.register(self.resources['BMany'])
        self.assertIn("bmanys", BResource.fields_to_many)
        self.assertEqual(BResource.fields_to_many["bmanys"]["name"], "bmanys")
        self.assertEqual(
            BResource.fields_to_many["bmanys"]["related_resource"],
            BManyResource)

    def test_fields_to_one_other_model_foreign_key_inheritance(self):
        AResource = self.api.register(self.resources['A'])
        BResource = self.api.register(self.resources['B'])
        AOneResource = self.api.register(self.resources['AOne'])
        self.assertIn("bs", AOneResource.fields_to_many)
        self.assertEqual(AOneResource.fields_to_many["bs"]["name"], "a_set")
        self.assertEqual(AOneResource.fields_to_many["as"]["related_resource"],
                         AResource)
        self.assertEqual(AOneResource.fields_to_many["bs"]["related_resource"],
                         BResource)


class TestResource(TestCase):
    def test_resource_name(self):
        self.assertEqual(AuthorResource.Meta.name, 'author')
        self.assertEqual(AuthorResource.Meta.name_plural, 'authors')

    def test_resource_fields_shortcuts(self):
        class TestResource(Resource):
            class Meta:
                name = 'test'

        TestResource.fields = {
            "own": {
                "type": Resource.FIELD_TYPES.OWN
            },
            "to_one": {
                "type": Resource.FIELD_TYPES.TO_ONE
            },
            "to_many": {
                "type": Resource.FIELD_TYPES.TO_MANY
            },
        }
        self.assertEqual(TestResource.fields_own, {
            "own": TestResource.fields["own"]
        })

        self.assertEqual(TestResource.fields_to_one, {
            "to_one": TestResource.fields["to_one"]
        })

        self.assertEqual(TestResource.fields_to_many, {
            "to_many": TestResource.fields["to_many"]
        })

    def test_resource_get_empty(self):
        c = Client()
        response = c.get(
            '/api/author/',
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        data_expected = {
            "authors": []
        }
        self.assertEqual(data, data_expected)

    @unittest.skip("Temporary skip")
    def test_resource_get(self):
        post = mixer.blend(PostWithPicture)
        c = Client()
        response = c.get(
            '/api/postwithpicture/',
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        data_expected = {
            "postwithpictures": [{
                "id": post.id,
                "title": post.title,
                "picture_url": post.picture_url
            }]
        }
        self.assertEqual(data, data_expected)
