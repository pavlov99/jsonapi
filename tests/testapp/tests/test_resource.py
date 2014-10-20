from django.test import TestCase
import json
import unittest

from django.db import models
from mixer.backend.django import mixer

from jsonapi.resource import Resource


class TestResource(TestCase):
    def test_resource_fields_shortcuts(self):
        class Acld(models.Model):
            field = models.IntegerField()

        class TestResource(Resource):
            class Meta:
                model = Acld

        TestResource.fields = {
            "own": {
                "type": Resource.FIELD_TYPES.OWN
            },
            "to_one": {
                "type": Resource.FIELD_TYPES.TO_ONE
            },
            "to_many": {
                "type": Resource.FIELD_TYPES.TO_MANY
            },
        }
        self.assertEqual(TestResource.fields_own, {
            "own": TestResource.fields["own"]
        })

        self.assertEqual(TestResource.fields_to_one, {
            "to_one": TestResource.fields["to_one"]
        })

        self.assertEqual(TestResource.fields_to_many, {
            "to_many": TestResource.fields["to_many"]
        })

    def test_resource_get_empty(self):
        response = self.client.get(
            '/api/author',
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        data_expected = {
            "authors": []
        }
        self.assertEqual(data, data_expected)

    def test_resource_own_fields_serialization(self):
        mixer.blend('testapp.author')
        response = self.client.get(
            '/api/author',
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(data["authors"]), 1)

    def test_resource_get(self):
        post = mixer.blend('testapp.post')
        response = self.client.get(
            '/api/post',
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        data_expected = {
            "posts": [{
                "id": post.id,
                "title": post.title,
                "links": {
                    "author": post.author_id,
                    "user": post.user_id,
                }
            }]
        }
        self.assertEqual(data, data_expected)
