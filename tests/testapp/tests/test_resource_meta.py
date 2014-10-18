""" Test resource creation and metaclass functionality.

In case of tests failure, these tests should be fixed first.

"""
from django.db import models
from django.test import TestCase
from jsonapi.django_utils import clear_app_cache
from jsonapi.resource import Resource
from django.contrib.auth.models import User, AbstractBaseUser
from mock import patch


class TestResourceMeta(TestCase):
    def setUp(self):
        class A(models.Model):
            field = models.IntegerField()

        class AResource(Resource):
            class Meta:
                model = A
                name = "a_name"

        class BResource(Resource):
            class Meta:
                name = "b"

        class UserResource(Resource):
            class Meta:
                model = User

        self.A = A
        self.AResource = AResource
        self.BResource = BResource
        self.UserResource = UserResource


    def tearDown(self):
        clear_app_cache('testapp')

    def test_resource_name(self):
        self.assertEqual(Resource.Meta.name, None)
        self.assertEqual(self.AResource.Meta.name, 'a_name')
        self.assertEqual(self.AResource.Meta.name_plural, 'a_names')
        self.assertEqual(self.BResource.Meta.name, 'b')
        self.assertEqual(self.BResource.Meta.name_plural, 'bs')

    def test_resource_is_model(self):
        self.assertTrue(self.AResource.Meta.is_model)
        self.assertFalse(self.BResource.Meta.is_model)

    def test_resource_model(self):
        self.assertEqual(self.AResource.Meta.model, self.A)
        self.assertFalse(hasattr(self.BResource.Meta, "model"))

    def test_is_auth_user(self):
        self.assertFalse(self.AResource.Meta.is_auth_user)
        self.assertTrue(self.UserResource.Meta.is_auth_user)

    def test_is_auth_user_inheritance(self):
        class CustomUser(AbstractBaseUser):
            pass

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
        class AChild(self.A):
            pass

        class AChildResource(Resource):
            class Meta:
                model = AChild

        self.assertFalse(self.AResource.Meta.is_inherited)
        self.assertFalse(self.UserResource.Meta.is_inherited)
        self.assertTrue(AChildResource.Meta.is_inherited)
