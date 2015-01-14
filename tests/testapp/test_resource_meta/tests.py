from django.contrib.auth.models import User
from django.test import TestCase
from jsonapi.resource import Resource
from .models import A, AChild


class TestResourceMeta(TestCase):
    def setUp(self):
        class AResource(Resource):
            class Meta:
                model = A

        class AChildResource(Resource):
            class Meta:
                model = AChild
                name = "ac"

        class BResource(Resource):
            class Meta:
                name = "b"

        class UserResource(Resource):
            class Meta:
                model = User

        self.AResource = AResource
        self.AChildResource = AChildResource
        self.BResource = BResource
        self.UserResource = UserResource

    def test_resource_name(self):
        self.assertEqual(Resource.Meta.name, None)
        self.assertEqual(self.AResource.Meta.name, 'a')
        self.assertEqual(self.AResource.Meta.name_plural, 'as')
        self.assertEqual(self.BResource.Meta.name, 'b')
        self.assertEqual(self.BResource.Meta.name_plural, 'bs')
        self.assertEqual(self.AChildResource.Meta.name, 'ac')
        self.assertEqual(self.AChildResource.Meta.name_plural, 'acs')

    def test_resource_is_model(self):
        self.assertTrue(self.AResource.Meta.is_model)
        self.assertFalse(self.BResource.Meta.is_model)

    def test_resource_model(self):
        self.assertEqual(self.AResource.Meta.model, A)
        self.assertFalse(hasattr(self.BResource.Meta, "model"))
