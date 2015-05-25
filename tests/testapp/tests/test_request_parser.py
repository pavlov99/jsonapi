""" Test parser of GET parameters."""
from django.test import TestCase
from django.http import QueryDict
import unittest

from jsonapi.request_parser import RequestParser


class TestRequestParser(TestCase):

    def test_parse_sort_empty(self):
        querydict = QueryDict("")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.sort, [])

    def test_parse_sort_one_param(self):
        querydict = QueryDict("sort=a")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.sort, ["a"])

    def test_parse_sort_two_param(self):
        querydict = QueryDict("sort=a,b")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.sort, ["a", "b"])

        querydict = QueryDict("sort=a,-b")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.sort, ["a", "-b"])

        querydict = QueryDict("sort=a&sort=b")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.sort, ["a", "b"])

    def test_parse_include_empty(self):
        querydict = QueryDict("")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.include, [])

    def test_parse_include_one(self):
        querydict = QueryDict("include=a")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.include, ["a"])

    def test_parse_include_complex(self):
        querydict = QueryDict("include=a,b,a.b&include=b.c.d")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.include, ["a", "b", "a.b", "b.c.d"])

    def test_parse_page_empty(self):
        querydict = QueryDict("")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.page, None)

    def test_parse_page(self):
        querydict = QueryDict("page=2")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.page, 2)

    def test_parse_fields_empty(self):
        querydict = QueryDict("")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.fields, [])

    def test_parse_fields_one_param(self):
        querydict = QueryDict("fields=a")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.fields, ["a"])

    def test_parse_fields_two_param(self):
        querydict = QueryDict("fields=a,b")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.fields, ["a", "b"])

        querydict = QueryDict("fields=a&fields=b")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.fields, ["a", "b"])

    def test_parse_fields_typed(self):
        querydict = QueryDict("fields[resource_1]=a&fields[resource2]=b,c")
        result = RequestParser.parse(querydict)
        expected_result = [
            ("resource_1", "a"),
            ("resource2", "b"),
            ("resource2", "c"),
        ]
        self.assertEqual(sorted(result.fields), sorted(expected_result))

    def test_parse_fields_typed_complex(self):
        querydict = QueryDict(
            "fields[resource2]=a&fields[resource1]=c&fields[resource2]=b")
        result = RequestParser.parse(querydict)
        expected_result = [
            ("resource2", "a"),
            ("resource1", "c"),
            ("resource2", "b"),
        ]
        self.assertEqual(sorted(result.fields), sorted(expected_result))

    def test_parse_fields_default_and_typed(self):
        querydict = QueryDict("fields=a&fields[a]=b")

        with self.assertRaises(ValueError):
            RequestParser.parse(querydict)

    def test_parse_filters(self):
        querydict = QueryDict("filter=a=1&filter=b__in=[1,2]&filter=c__gt=0" +
                              "&fields=a&sort=b&include=c&page=1")
        result = RequestParser.parse(querydict)
        self.assertEqual(result.filter, ['a=1', 'b__in=[1,2]', 'c__gt=0'])
