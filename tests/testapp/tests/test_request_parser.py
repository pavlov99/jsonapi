""" Test parser of GET parameters."""
from django.test import TestCase
from django.http import QueryDict
from jsonapi.request_parser import RequestParser


class TestRequestParser(TestCase):

    def test_parse_filters(self):
        pass

    def test_parse_sort_empty(self):
        querydict = {}
        result = RequestParser.parse(querydict)
        self.assertEqual(result["sort"], None)

    def test_parse_sort_one_param(self):
        querydict = {"sort": ["a"]}
        result = RequestParser.parse(querydict)
        self.assertEqual(result["sort"], ["a"])

    def test_parse_sort_two_param(self):
        querydict = {"sort": ["a", "b"]}
        result = RequestParser.parse(querydict)
        self.assertEqual(result["sort"], ["a", "b"])

        query = "sort=a,b"
        querydict = dict(QueryDict(query).iterlists())
        result = RequestParser.parse(querydict)
        self.assertEqual(result["sort"], ["a", "b"])

        query = "sort=a,-b"
        querydict = dict(QueryDict(query).iterlists())
        result = RequestParser.parse(querydict)
        self.assertEqual(result["sort"], ["a", "-b"])

        query = "sort=a&sort=b"
        querydict = dict(QueryDict(query).iterlists())
        result = RequestParser.parse(querydict)
        self.assertEqual(result["sort"], ["a", "b"])

    def test_parse_sort_typed(self):
        query = "sort[resource1]=a&sort[resource2]=b,c"
        querydict = dict(QueryDict(query).iterlists())
        result = RequestParser.parse(querydict)
        expected_result = {
            "resource1": ["a"],
            "resource2": ["b", "c"],
        }
        self.assertEqual(result["sort"], expected_result)

    def test_parse_include(self):
        pass

    def test_parse_page(self):
        pass
