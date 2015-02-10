from django.test import TestCase
from jsonapi.api import API
from jsonapi.resource import Resource
from mixer.backend.django import mixer
import django
import unittest
import json

from ..models import Author
from ..urls import api


class TestApi(TestCase):
    # NOTE: if use django-admin command --top-level-directory, need to specify
    # urls = 'testapp.url', otherwise api is created two times (different
    # obbjects), tests are failed. After specification TEST_DISCOVER_TOP_LEVEL
    # in settings, this line is not required.
    # urls = 'testapp.urls'

    def setUp(self):
        self.api = API()

    def test_resource_registration(self):
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.api.register(TestResource)
        self.assertEqual(self.api.resource_map['test'], TestResource)

    def test_resource_registration_decorator(self):
        @self.api.register
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.assertEqual(self.api.resource_map['test'], TestResource)

    def test_resource_registration_decorator_params(self):
        @self.api.register()
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.assertEqual(self.api.resource_map['test'], TestResource)

    def test_meta_params_add_during_registration(self):
        @self.api.register(name='test', param='param')
        class TestResource(Resource):
            class Meta:
                name = '_test'

        self.assertEqual(self.api.resource_map['test'], TestResource)
        self.assertEqual(TestResource.Meta.name, 'test')
        self.assertEqual(TestResource.Meta.param, 'param')

    def test_recource_api_reference(self):
        class TestResource(Resource):
            class Meta:
                name = 'test'

        self.assertFalse(hasattr(TestResource.Meta, 'api'))
        self.api.register(TestResource)
        self.assertTrue(TestResource.Meta.api is self.api)

    def test_resource_name_collapse_same_name(self):
        class NewsResource(Resource):
            class Meta:
                name = 'news'

        class NewsOtherResource(Resource):
            class Meta:
                name = 'news'

        self.api.register(NewsResource)
        with self.assertRaises(ValueError):
            # The same resource name
            self.api.register(NewsOtherResource)

        NewsOtherResource.Meta.name = "allowed"
        with self.assertRaises(ValueError):
            # The same resource name
            self.api.register(NewsOtherResource, name='news')

    def test_resource_name_collapse_with_plural(self):
        class NewsResource(Resource):
            class Meta:
                name = 'news'

        class NewResource(Resource):
            class Meta:
                name = 'new'

        self.api.register(NewsResource)
        with self.assertRaises(ValueError):
            # NewResource.name_plural = NewsResource.name
            self.api.register(NewResource)

        NewResource.Meta.name = "allowed"
        with self.assertRaises(ValueError):
            # NewResource.name_plural = NewsResource.name
            self.api.register(NewResource, name='new')

    def test_resource_name_collapse_with_singular(self):
        class NewsResource(Resource):
            class Meta:
                name = 'news'

        class NewssResource(Resource):
            class Meta:
                name = 'newss'

        self.api.register(NewsResource)
        with self.assertRaises(ValueError):
            # NewsResource.name_plural = NewssResource.name
            self.api.register(NewssResource)

        NewssResource.Meta.name = "allowed"
        with self.assertRaises(ValueError):
            # NewsResource.name_plural = NewssResource.name
            self.api.register(NewssResource, name="newss")

    def test_resource_name(self):
        class AResource(Resource):
            class Meta:
                name = 'a'

        self.api.register(AResource)
        AResource.Meta.name = 'b'
        self.assertEqual(AResource.Meta.name_plural, 'bs')
        self.assertEqual(self.api.resource_map['b'], AResource)
        self.assertNotIn('a', self.api.resource_map)

    @unittest.skip("Not implemented")
    def test_content_type_validation(self):
        response = self.client.get('/api', content_type='application/json')
        self.assertEqual(response.status_code, 415)
        self.assertEqual(
            str(response.content),
            "Content-Type SHOULD be application/vnd.api+json")

    @unittest.skipIf(django.VERSION[:2] == (1, 5),
                     "FIXME: For some reason does not work. Tested manually")
    def test_base_url(self):
        self.client.get('/api', content_type='application/vnd.api+json')
        self.assertEqual(api.base_url, "http://testserver")

    @unittest.skipIf(django.VERSION[:2] == (1, 5),
                     "FIXME: For some reason does not work. Tested manually")
    def test_api_url(self):
        self.client.get('/api', content_type='application/vnd.api+json')
        self.assertEqual(api.api_url, "http://testserver/api")


class TestApiClient(TestCase):
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

        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.get()

        expected_data = {
            "authors": {
                "id": author.id,
                "name": author.name,
            }
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(author.name, "author")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertTrue(response.has_header("Location"))

        location = "http://testserver/api/author/{}".format(author.id)
        self.assertEqual(response["Location"], location)

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
        authors = Author.objects.all()
        authors_names = Author.objects.values_list('name', flat=True)
        self.assertEqual(set(authors_names), {"author1", "author2", "author3"})

        expected_data = {
            "authors": [{
                "id": author.id,
                "name": author.name,
            } for author in authors]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertTrue(response.has_header("Location"))

        location = "http://testserver/api/author/1,2,3"
        self.assertEqual(response["Location"], location)

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

    def test_update_model_missing_ids(self):
        mixer.blend("testapp.author")
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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "Request SHOULD have resource ids")

    def test_delete_model(self):
        author = mixer.blend("testapp.author")
        response = self.client.delete(
            '/api/author/{}'.format(author.id),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Author.objects.count(), 0)

    def test_delete_models(self):
        authors = mixer.cycle(2).blend("testapp.author")
        response = self.client.delete(
            '/api/author/{}'.format(",".join([str(a.id) for a in authors])),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Author.objects.count(), 0)

    def test_delete_model_missing_ids(self):
        response = self.client.delete(
            '/api/author',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "Request SHOULD have resource ids")

    def test_get_top_level_links(self):
        post = mixer.blend("testapp.post")
        response = self.client.get(
            '/api/post',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "posts": [{
                "id": post.id,
                "title": post.title,
                "links": {
                    "user": post.user_id,
                    "author": post.author_id,
                }
            }],
            "links": {
                "posts.author": "http://testserver/api/author/{posts.author}",
                "posts.user": "http://testserver/api/user/{posts.user}",
            }
        }

        self.maxDiff = None
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_get_include(self):
        post = mixer.blend("testapp.post")
        response = self.client.get(
            '/api/post?include=author',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))["linked"]
        expected_data = {
            "authors": [{
                "id": post.author_id,
                "name": post.author.name
            }]
        }
        self.assertEqual(data, expected_data)

    def test_get_include_null(self):
        """ Test include optional foreign key field."""
        post1 = mixer.blend("testapp.post")
        post2 = mixer.blend("testapp.post", user__username="username")
        user = post2.user
        response = self.client.get(
            '/api/post?include=user',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        expected_data = {
            "posts": [{
                "id": post.id,
                "title": post.title,
                "links": {
                    "author": post.author_id,
                    "user": post.user_id,
                }
            } for post in [post1, post2]],
            "linked": {
                "users": [{
                    "id": user.id,
                    "date_joined": user.date_joined.isoformat(),
                    "email": user.email,
                    'first_name': user.first_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'last_login': user.last_login.isoformat(),
                    'last_name': user.last_name,
                    'username': user.username,
                }]
            },
            'links': {
                'posts.author': 'http://testserver/api/author/{posts.author}',
                'posts.user': 'http://testserver/api/user/{posts.user}'
            },
        }
        self.maxDiff = None
        self.assertEqual(data, expected_data)

    def test_get_include_many(self):
        comment = mixer.blend("testapp.comment")
        response = self.client.get(
            '/api/post?include=comments',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))["linked"]
        expected_data = {
            "comments": [{
                "id": comment.id,
                "links": {
                    "author": comment.author_id,
                    "post": comment.post_id,
                },
            }]
        }
        self.assertEqual(data, expected_data)

    def test_get_include_fields(self):
        mixer.blend("testapp.postwithpicture")
        response = self.client.get(
            '/api/postwithpicture',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("title_uppercased", data["postwithpictures"][0])

        response = self.client.get(
            '/api/post',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertNotIn("title_uppercased", data["posts"][0])

    def test_get_exclude_fields(self):
        mixer.blend("testapp.postwithpicture")
        response = self.client.get(
            '/api/postwithpicture',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertNotIn("title", data["postwithpictures"][0])
