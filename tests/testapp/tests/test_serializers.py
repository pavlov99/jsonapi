from django.test import TestCase
from django.db import models
#from django.db.models.loading import cache
from mixer.backend.django import mixer

from jsonapi.serializers import Serializer


class TestSerializers(TestCase):
    def setUp(self):
        class A(models.Model):
            a1 = models.CharField(max_length=100)
            a2 = models.IntegerField()

        class B(A):
            b = models.IntegerField()

        class C(models.Model):
            bs = models.ManyToManyField(B)

        class D(models.Model):
            c = models.ForeignKey(C)

        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def tearDown(self):
        # Delete models from django cache
        del models.loading.cache.app_models['tests']

    def test_get_id(self):
        author = mixer.blend('testapp.author')
        self.assertEqual(author.pk, Serializer.get_id(author))

    def test_get_id_inheritance(self):
        post = mixer.blend('testapp.postwithpicture')
        self.assertEqual(post.pk, Serializer.get_id(post))

    def test_fields(self):
        fields = Serializer.get_fields(self.A)
        field_names = {f.name for f in fields}
        self.assertIn('a1', field_names)
        self.assertIn('a2', field_names)

    def test_fields_inheritance(self):
        fields = Serializer.get_fields(self.B)
        field_names = {f.name for f in fields}
        self.assertIn('a1', field_names)
        self.assertIn('a2', field_names)
        self.assertIn('b', field_names)

    def test_fields_many_to_many(self):
        fields = Serializer.get_fields(self.C)
        field_names = {f.name for f in fields}
        self.assertIn('bs', field_names)

    def test_fields_foreign_key(self):
        fields = Serializer.get_fields(self.D)
        field_names = {f.name for f in fields}
        self.assertIn('c', field_names)
