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
        query = "sort[resource_1]=a&sort[resource2]=b,c"
        result = RequestParser.parse(query)
        expected_result = [
            ("resource_1", "a"),
            ("resource2", "b"),
            ("resource2", "c"),
        ]
        self.assertEqual(set(result["sort"]), set(expected_result))

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

    def test_parse_include_empty(self):
        query = ""
        result = RequestParser.parse(query)
        self.assertEqual(result["include"], [])

    def test_parse_include_one(self):
        query = "include=a"
        result = RequestParser.parse(query)
        self.assertEqual(result["include"], ["a"])

    def test_parse_include_complex(self):
        query = "include=a,b,a.b"
        result = RequestParser.parse(query)
        self.assertEqual(result["include"], ["a", "b", "a.b"])

    def test_parse_page_empty(self):
        query = ""
        result = RequestParser.parse(query)
        self.assertEqual(result["page"], None)

    def test_parse_page(self):
        query = "page=1"
        result = RequestParser.parse(query)
        self.assertEqual(result["page"], 1)

    def test_parse_fields_empty(self):
        query = ""
        result = RequestParser.parse(query)
        self.assertEqual(result["fields"], [])

    def test_parse_fields_one_param(self):
        query = "fields=a"
        result = RequestParser.parse(query)
        self.assertEqual(result["fields"], ["a"])

    def test_parse_fields_two_param(self):
        query = "fields=a,b"
        result = RequestParser.parse(query)
        self.assertEqual(result["fields"], ["a", "b"])

        query = "fields=a&fields=b"
        result = RequestParser.parse(query)
        self.assertEqual(result["fields"], ["a", "b"])

    def test_parse_fields_typed(self):
        query = "fields[resource_1]=a&fields[resource2]=b,c"
        result = RequestParser.parse(query)
        expected_result = [
            ("resource_1", "a"),
            ("resource2", "b"),
            ("resource2", "c"),
        ]
        self.assertEqual(sorted(result["fields"]), sorted(expected_result))

    @unittest.skip("Not Implemented. Requires custom query parser")
    def test_parse_fields_typed_complex(self):
        query = "fields[resource2]=a&fields[resource1]=c&fields[resource2]=b"
        result = RequestParser.parse(query)
        expected_result = [
            ("resource2", "a"),
            ("resource1", "c"),
            ("resource2", "b"),
        ]
        self.assertEqual(result["fields"], expected_result)

    def test_parse_fields_default_and_typed(self):
        query = "fields=a&fields[a]=b"
        # TODO: define concrete error
        with self.assertRaises(ValueError):
            RequestParser.parse(query)

    def test_parse_filters(self):
        query = "a=1&b__in=[1,2]&c__gt=0&fields=a&sort=b&include=c&page=1"
        result = RequestParser.parse(query)
        self.assertEqual(
            result["filters"], {"a": "1", "b__in": "[1,2]", "c__gt": "0"})
