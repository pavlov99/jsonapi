from django.test import TestCase
from jsonapi.resource import Resource
from ..models import A, B


class TestResourceMeta(TestCase):
    def setUp(self):
        class AResource(Resource):
            class Meta:
                model = A

        class BResource(Resource):
            class Meta:
                model = B
                name = "bb"

        class CResource(Resource):
            class Meta:
                name = "c"

        self.AResource = AResource
        self.BResource = BResource
        self.CResource = CResource

    def test_resource_name(self):
        self.assertEqual(Resource.Meta.name, None)
        self.assertEqual(self.AResource.Meta.name, 'a')
        self.assertEqual(self.AResource.Meta.name_plural, 'as')
        self.assertEqual(self.BResource.Meta.name, 'bb')
        self.assertEqual(self.BResource.Meta.name_plural, 'bbs')
        self.assertEqual(self.CResource.Meta.name, 'c')
        self.assertEqual(self.CResource.Meta.name_plural, 'cs')

    def test_resource_is_model(self):
        self.assertTrue(self.AResource.Meta.is_model)
        self.assertFalse(self.CResource.Meta.is_model)

    def test_resource_model(self):
        self.assertEqual(self.AResource.Meta.model, A)
        self.assertFalse(hasattr(self.CResource.Meta, "model"))
