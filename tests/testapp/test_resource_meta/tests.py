from django.contrib.auth.models import User
from django.test import TestCase
from jsonapi.resource import Resource
from mock import patch

from .models import CustomUser, A, AChild


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

    def test_is_auth_user(self):
        self.assertFalse(self.AResource.Meta.is_auth_user)
        self.assertTrue(self.UserResource.Meta.is_auth_user)

    def test_is_auth_user_inheritance(self):
        class CustomUserResource(Resource):
            class Meta:
                model = CustomUser

        self.assertTrue(self.UserResource.Meta.is_auth_user)
        self.assertFalse(CustomUserResource.Meta.is_auth_user)

        with patch('jsonapi.resource.ResourceManager') as mock_manager:
            mock_manager.get_concrete_model_by_name.return_value = CustomUser
            self.assertFalse(self.UserResource.Meta.is_auth_user)
            self.assertTrue(CustomUserResource.Meta.is_auth_user)

    def test_is_inherited(self):
        self.assertFalse(self.AResource.Meta.is_inherited)
        self.assertFalse(self.UserResource.Meta.is_inherited)
        self.assertTrue(self.AChildResource.Meta.is_inherited)
