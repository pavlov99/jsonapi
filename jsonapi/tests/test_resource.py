import unittest
from ..resource import Resource, ResourceManager
from .myapp.models import Author


class TestResource(unittest.TestCase):
    def setUp(self):
        self.objects = [
            {"id": 1, "name": "name"}
        ]

        class StaticResource(Resource):
            def get(self_):
                return self.objects
        self.static_resource = StaticResource()

    def test_static_resource(self):
        self.assertEqual(self.static_resource.get(), self.objects)

    def test_django_resource_name(self):
        class AuthorResource(Resource):
            class Meta:
                model = Author

        self.assertEqual(AuthorResource.Meta.name, 'author')
