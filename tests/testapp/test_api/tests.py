from django.test import TestCase
from jsonapi.api import API
from jsonapi.resource import Resource
import unittest
import django

from ..urls import api


class TestApi(TestCase):
    # NOTE: if use django-admin command --top-level-directory, need to specify
    # urls = 'testapp.url', otherwise api is created two times (different
    # obbjects), tests are failed. After specification TEST_DISCOVER_TOP_LEVEL
    # in settings, this line is not required.
    # urls = 'testapp.urls'

    def setUp(self):
        self.api = API()

    def test_resource_registration(self):
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.api.register(TestResource)
        self.assertEqual(self.api.resource_map['test'], TestResource)

    def test_resource_registration_decorator(self):
        @self.api.register
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.assertEqual(self.api.resource_map['test'], TestResource)

    def test_resource_registration_decorator_params(self):
        @self.api.register()
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.assertEqual(self.api.resource_map['test'], TestResource)

    def test_meta_params_add_during_registration(self):
        @self.api.register(name='test', param='param')
        class TestResource(Resource):
            class Meta:
                name = '_test'

        self.assertEqual(self.api.resource_map['test'], TestResource)
        self.assertEqual(TestResource.Meta.name, 'test')
        self.assertEqual(TestResource.Meta.param, 'param')

    def test_recource_api_reference(self):
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.assertFalse(hasattr(TestResource.Meta, 'api'))
        self.api.register(TestResource)
        self.assertTrue(TestResource.Meta.api is self.api)

    def test_resource_name_collapse_same_name(self):
        class NewsResource(Resource):
            class Meta:
                name = 'news'

        class NewsOtherResource(Resource):
            class Meta:
                name = 'news'

        self.api.register(NewsResource)
        with self.assertRaises(ValueError):
            # The same resource name
            self.api.register(NewsOtherResource)

        NewsOtherResource.Meta.name = "allowed"
        with self.assertRaises(ValueError):
            # The same resource name
            self.api.register(NewsOtherResource, name='news')

    def test_resource_name_collapse_with_plural(self):
        class NewsResource(Resource):
            class Meta:
                name = 'news'

        class NewResource(Resource):
            class Meta:
                name = 'new'

        self.api.register(NewsResource)
        with self.assertRaises(ValueError):
            # NewResource.name_plural = NewsResource.name
            self.api.register(NewResource)

        NewResource.Meta.name = "allowed"
        with self.assertRaises(ValueError):
            # NewResource.name_plural = NewsResource.name
            self.api.register(NewResource, name='new')

    def test_resource_name_collapse_with_singular(self):
        class NewsResource(Resource):
            class Meta:
                name = 'news'

        class NewssResource(Resource):
            class Meta:
                name = 'newss'

        self.api.register(NewsResource)
        with self.assertRaises(ValueError):
            # NewsResource.name_plural = NewssResource.name
            self.api.register(NewssResource)

        NewssResource.Meta.name = "allowed"
        with self.assertRaises(ValueError):
            # NewsResource.name_plural = NewssResource.name
            self.api.register(NewssResource, name="newss")

    def test_resource_name(self):
        class AResource(Resource):
            class Meta:
                name = 'a'

        self.api.register(AResource)
        AResource.Meta.name = 'b'
        self.assertEqual(AResource.Meta.name_plural, 'bs')
        self.assertEqual(self.api.resource_map['b'], AResource)
        self.assertNotIn('a', self.api.resource_map)

    @unittest.skip("Not implemented")
    def test_content_type_validation(self):
        response = self.client.get('/api', content_type='application/json')
        self.assertEqual(response.status_code, 415)
        self.assertEqual(
            str(response.content), "Content-Type SHOULD be application/vnd.api+json")

    @unittest.skipIf(django.VERSION[:2] == (1, 5),
                     "FIXME: For some reason does not work. Tested manually")
    def test_base_url(self):
        self.client.get('/api', content_type='application/vnd.api+json')
        self.assertEqual(api.base_url, "http://testserver")

    @unittest.skipIf(django.VERSION[:2] == (1, 5),
                     "FIXME: For some reason does not work. Tested manually")
    def test_api_url(self):
        self.client.get('/api', content_type='application/vnd.api+json')
        self.assertEqual(api.api_url, "http://testserver/api")
