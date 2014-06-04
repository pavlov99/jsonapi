import unittest
from ..resource import Resource
from .myapp.models import Author


class TestResource(unittest.TestCase):
    def setUp(self):
        class StaticResource(Resource):
            def get(self):
                objects = [
                    {"id": 1, "name": "name"}
                ]
                return objects
        self.static_resource = StaticResource()

    def test_django_resource_name(self):
        class AuthorResource(Resource):
            class Meta:
                model = Author

        self.assertEqual(AuthorResource.Meta.name, 'author')
