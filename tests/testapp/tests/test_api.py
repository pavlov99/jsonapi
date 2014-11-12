from django.test import TestCase
from ..models import Author


class TestApiClient(TestCase):
    def test_create_model(self):
        self.assertEqual(Author.objects.count(), 0)
        response = self.client.post(
            '/api/author',
            {
                "authors": [
                    {"name": "author"},
                ]
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
