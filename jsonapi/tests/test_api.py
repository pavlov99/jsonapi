import unittest

from ..api import API
from ..resource import Resource
from .myapp.models import Author


class TestApi(unittest.TestCase):
    def setUp(self):
        self.api = API()

        class AuthorResource(Resource):
            class Meta:
                model = Author

        self.author_resource = AuthorResource
        self.api.register(AuthorResource)

    def test_resource_map(self):
        self.assertEqual(len(self.api.resource_map), 1)
        self.assertIn('author', self.api.resource_map)
