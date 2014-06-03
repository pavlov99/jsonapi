import unittest
from ..resource import Resource


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
