""" Test parser of GET parameters."""
from django.test import TestCase
import unittest

from jsonapi.request_parser import RequestParser


class TestRequestParser(TestCase):

    def test_parse_sort_empty(self):
        query = ""
        result = RequestParser.parse(query)
        self.assertEqual(result["sort"], [])

    def test_parse_sort_one_param(self):
        query = "sort=a"
        result = RequestParser.parse(query)
        self.assertEqual(result["sort"], ["a"])

    def test_parse_sort_two_param(self):
        query = "sort=a,b"
        result = RequestParser.parse(query)
        self.assertEqual(result["sort"], ["a", "b"])

        query = "sort=a,-b"
        result = RequestParser.parse(query)
        self.assertEqual(result["sort"], ["a", "-b"])

        query = "sort=a&sort=b"
        result = RequestParser.parse(query)
        self.assertEqual(result["sort"], ["a", "b"])

    def test_parse_sort_typed(self):
        query = "sort[resource1]=a&sort[resource2]=b,c"
        result = RequestParser.parse(query)
        expected_result = [
            ("resource1", "a"),
            ("resource2", "b"),
            ("resource2", "c"),
        ]
        self.assertEqual(result["sort"], expected_result)

    @unittest.skip("Not Implemented. Requires custom query parser")
    def test_parse_sort_typed_complex(self):
        query = "sort[resource2]=-a&sort[resource1]=-c&sort[resource2]=b"
        result = RequestParser.parse(query)
        expected_result = [
            ("resource2", "-a"),
            ("resource1", "-c"),
            ("resource2", "b"),
        ]
        self.assertEqual(result["sort"], expected_result)

    def test_parse_sort_default_and_typed(self):
        query = "sort=a&sort[a]=b"
        # TODO: define concrete error
        with self.assertRaises(ValueError):
            RequestParser.parse(query)

    def test_parse_filters(self):
        pass

    def test_parse_include(self):
        pass

    def test_parse_page(self):
        pass
