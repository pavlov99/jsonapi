from django.test import TestCase
from django.db import models

from jsonapi.serializers import Serializer


FIELDS = (
    models.BigIntegerField,
    models.BinaryField,
    models.BooleanField,
    models.CharField,
    models.CommaSeparatedIntegerField,
    models.DateField,
    models.DateTimeField,
    models.DecimalField,
    models.EmailField,
    models.FileField,
    models.FilePathField,
    models.FloatField,
    models.ImageField,
    models.IntegerField,
    models.IPAddressField,
    models.GenericIPAddressField,
    models.NullBooleanField,
    models.PositiveIntegerField,
    models.PositiveSmallIntegerField,
    models.SlugField,
    models.SmallIntegerField,
    models.TextField,
    models.TimeField,
    models.URLField,
)


class TestSerializers(TestCase):
    def setUp(self):
        class A(models.Model):
            a = models.CharField(max_length=100)

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

    def test_dump_document_field_redefinition(self):
        obj = self.A(a="a")
        fields = {
            "id": {"name": "id"},
            "a": {"name": "a"},
        }
        obj_dump = Serializer.dump_document(obj, fields)
        expected_dump = {
            "id": obj.id,
            "a": "a",
        }
        self.assertEqual(obj_dump, expected_dump)

        Serializer.dump_document_a = staticmethod(lambda value: None)
        obj_dump = Serializer.dump_document(obj, fields)
        expected_dump["a"] = None
        self.assertEqual(obj_dump, expected_dump)
