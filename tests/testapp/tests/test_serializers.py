from django.test import TestCase
from mixer.backend.django import mixer
import datetime
import decimal
import json

from jsonapi.serializers import Serializer, DatetimeDecimalEncoder

from ..models import TestSerializerAllFields


class TestSerializers(TestCase):
    def setUp(self):
        Serializer.Meta.api = type(
            'Api', (object,), {"base_url": "http://testserver"})
        self.obj = mixer.blend(TestSerializerAllFields)

    def test_django_fields_serialization(self):
        fields_own = [
            f.name for f in self.obj._meta.fields if f.serialize
        ]
        obj = Serializer.dump_document(self.obj, fields_own=fields_own)

        self.assertEqual(obj['big_integer'], self.obj.big_integer)
        self.assertEqual(obj['boolean'], self.obj.boolean)
        self.assertEqual(obj['char'], self.obj.char)
        self.assertEqual(obj['comma_separated_integer'], [
            x for x in self.obj.comma_separated_integer
        ])
        self.assertEqual(obj['date'], self.obj.date)
        self.assertEqual(obj['datetime'], self.obj.datetime)
        self.assertEqual(obj['decimal'], self.obj.decimal)
        self.assertEqual(obj['email'], self.obj.email)
        self.assertEqual(
            obj['authorfile'],
            "http://testserver{}".format(self.obj.authorfile.url))
        self.assertEqual(obj['filepath'], self.obj.filepath)
        self.assertEqual(obj['floatnum'], self.obj.floatnum)
        self.assertEqual(obj['integer'], self.obj.integer)
        self.assertEqual(obj['ip'], self.obj.ip)
        self.assertEqual(obj['generic_ip'], self.obj.generic_ip)
        self.assertEqual(obj['nullboolean'], self.obj.nullboolean)
        self.assertEqual(obj['positive_integer'], self.obj.positive_integer)
        self.assertEqual(
            obj['positive_small_integer'], self.obj.positive_small_integer)
        self.assertEqual(obj['slug'], self.obj.slug)
        self.assertEqual(obj['small_integer'], self.obj.small_integer)
        self.assertEqual(obj['text'], self.obj.text)
        self.assertEqual(obj['time'], self.obj.time)
        self.assertEqual(obj['url'], self.obj.url)

    def test_dump_document_field_redefinition(self):
        fields_own = [name for name in ["id", "char"]]
        obj_dump = Serializer.dump_document(self.obj, fields_own)
        expected_dump = {
            "id": self.obj.id,
            "char": self.obj.char,
        }
        self.assertEqual(obj_dump, expected_dump)

        Serializer.dump_document_char = staticmethod(lambda obj: None)
        obj_dump = Serializer.dump_document(self.obj, fields_own)
        expected_dump["char"] = None
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
