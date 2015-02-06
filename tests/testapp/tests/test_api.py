from django.test import TestCase
from mixer.backend.django import mixer
from ..models import Author
import unittest


class TestApiClient(TestCase):
    def test_create_model(self):
        self.assertEqual(Author.objects.count(), 0)
        # NOTE: send individual resource
        response = self.client.post(
            '/api/author',
            {
                "authors": {
                    "name": "author"
                },
            },
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.get()
        self.assertEqual(author.name, "author")

    def test_create_models(self):
        self.assertEqual(Author.objects.count(), 0)
        # TODO: try to decrease number of queries
        # NOTE: send resource collection
        with self.assertNumQueries(3):
            response = self.client.post(
                '/api/author',
                {
                    "authors": [
                        {"name": "author1"},
                        {"name": "author2"},
                        {"name": "author3"},
                    ]
                },
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Author.objects.count(), 3)
        authors_names = Author.objects.values_list('name', flat=True)
        self.assertEqual(set(authors_names), {"author1", "author2", "author3"})

    def test_update_model(self):
        author = mixer.blend("testapp.author", name="")
        response = self.client.put(
            '/api/author/{}'.format(author.id),
            {
                "authors": {
                    "id": author.id,
                    "name": "author",
                },
            },
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.get()
        self.assertEqual(author.name, "author")

    def test_update_models(self):
        authors = mixer.cycle(2).blend("testapp.author", name="")
        response = self.client.put(
            '/api/author/{}'.format(",".join([str(a.id) for a in authors])),
            {
                "authors": [{
                    "id": a.id,
                    "name": "author",
                } for a in authors],
            },
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 2)
        for author in Author.objects.all():
            self.assertEqual(author.name, "author")

    @unittest.skip("Not Implemented")
    def test_update_model_missing_ids(self):
        author = mixer.blend("testapp.author")
        response = self.client.put(
            '/api/author',
            {
                "authors": {
                    "name": "author"
                },
            },
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 201)
