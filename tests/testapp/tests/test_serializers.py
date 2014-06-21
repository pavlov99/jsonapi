from django.db import models
from django.test import TestCase
import datetime
import decimal
import json

from jsonapi.serializers import Serializer, DatetimeDecimalEncoder


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


class DatetimeDecimalEncoderTest(TestCase):
    def test_datetime_serialization(self):
        obj = datetime.datetime(1900, 12, 31, 23, 59, 0)
        s = json.dumps(obj, cls=DatetimeDecimalEncoder)
        self.assertEqual(s, '"1900-12-31T23:59:00"')

    def test_date_serialization(self):
        obj = datetime.date(1900, 12, 31)
        s = json.dumps(obj, cls=DatetimeDecimalEncoder)
        self.assertEqual(s, '"1900-12-31"')

    def test_time_serialization(self):
        obj = datetime.time(23, 59, 0, 1)
        s = json.dumps(obj, cls=DatetimeDecimalEncoder)
        self.assertEqual(s, '"23:59:00.000001"')

    def test_decimal_serialization(self):
        obj = decimal.Decimal('0.1')
        s = json.dumps(obj, cls=DatetimeDecimalEncoder)
        self.assertEqual(float(s), float(0.1))
