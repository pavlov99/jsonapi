from django.test import TestCase
import json

from django.test import Client
from django.db import models
from mixer.backend.django import mixer

from jsonapi.resource import Resource
from tests.testapp.models import PostWithPicture
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
            b = models.ForeignKey(B)

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

    def tearDown(self):
        del models.loading.cache.app_models['tests']

    def test_abstract_model_resource(self):
        with self.assertRaises(ValueError):
            class AAbstractResource(Resource):
                class Meta:
                    model = self.classes['AAbstract']

    def test_resource_fields(self):
        fields = PostWithPictureResource.Meta.fields
        self.assertTrue(isinstance(fields, dict))


class TestResource(TestCase):
    def test_resource_name(self):
        self.assertEqual(AuthorResource.Meta.name, 'author')
        self.assertEqual(AuthorResource.Meta.name_plural, 'authors')

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
