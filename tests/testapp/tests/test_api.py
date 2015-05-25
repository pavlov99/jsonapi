from django.contrib.auth import get_user_model
from django.test import TestCase
from jsonapi.api import API
from jsonapi.resource import Resource
from mixer.backend.django import mixer
from testfixtures import compare
import json
import unittest
import datetime

from ..models import Author, Post, PostWithPicture
from ..urls import api

User = get_user_model()


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

    def test_base_url(self):
        self.client.get('/api', content_type='application/vnd.api+json')
        self.assertEqual(api.base_url, "http://testserver")

    def test_api_url(self):
        self.client.get('/api', content_type='application/vnd.api+json')
        self.assertEqual(api.api_url, "http://testserver/api")


class TestApiClient(TestCase):
    def setUp(self):
        self.user = mixer.blend(User)
        self.user.set_password('password')
        self.user.save()
        self.client.login(username=self.user.username, password='password')

    def test_resource_get_empty(self):
        response = self.client.get(
            '/api/author',
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        data_expected = {
            "data": []
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
        self.assertEqual(len(data["data"]), 1)

    def test_get_child_model(self):
        post = mixer.blend("testapp.postwithpicture", title="post")
        response = self.client.get(
            '/api/postwithpicture/{}'.format(post.id),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        expected_data = {
            "data": [{
                "id": post.id,
                "picture_url": post.picture_url,
                "title_uppercased": post.title.upper(),
                "dummy": "dummy",
                "links": {
                    "user": post.user and post.user.id,
                    "author": post.author and post.author.id
                }
            }]
        }
        data = json.loads(response.content.decode("utf-8"))
        compare(data["data"], expected_data["data"])

    def test_create_model(self):
        self.assertEqual(Author.objects.count(), 0)
        # NOTE: send individual resource
        response = self.client.post(
            '/api/author',
            json.dumps({
                "data": {
                    "name": "author"
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.get()

        expected_data = {
            "data": {
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
        with self.assertNumQueries(5):
            response = self.client.post(
                '/api/author',
                json.dumps({
                    "data": [
                        {"name": "author1"},
                        {"name": "author2"},
                        {"name": "author3"},
                    ]
                }),
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Author.objects.count(), 3)
        authors = Author.objects.all()
        authors_names = Author.objects.values_list('name', flat=True)
        self.assertEqual(set(authors_names), {"author1", "author2", "author3"})

        expected_data = {
            "data": [{
                "id": author.id,
                "name": author.name,
            } for author in authors]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertTrue(response.has_header("Location"))

        location = "http://testserver/api/author/1,2,3"
        self.assertEqual(response["Location"], location)

    def test_create_model_partial_generated_form(self):
        """ Post does not require user, it could be omitted."""
        author = mixer.blend('testapp.author')
        response = self.client.post(
            '/api/post',
            json.dumps({
                "data": {
                    "title": "title",
                    "links": {
                        "author": author.id
                    }
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 201)

        post = Post.objects.get()
        expected_data = {
            "data": {
                "id": post.id,
                "title": "title",
                "links": {
                    "author": author.id,
                    "user": None
                }
            }
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_create_model_validation_error(self):
        author = mixer.blend('testapp.author')
        response = self.client.post(
            '/api/post',
            json.dumps({
                "data": {
                    "links": {"author": author.id}
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32101,
                "title": "Model form validation error",
                "detail": '',
                "links": ['/data/0'],
                "paths": ['/title'],
                "data": {'title': ['This field is required.']},
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

        response = self.client.post(
            '/api/post',
            json.dumps({
                "data": {
                    "title": "New Post"
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32101,
                "title": "Model form validation error",
                "detail": '',
                "links": ['/data/0'],
                "paths": ['/author'],
                "data": {'author': ['This field is required.']},
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_create_models_validation_error(self):
        """ Ensure models are not created if one of them is not validated."""
        response = self.client.post(
            '/api/author',
            json.dumps({
                "data": [{
                    "name": "short name"
                }, {
                    "name": "long name" * 20
                }],
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32101,
                "title": "Model form validation error",
                "detail": '',
                "links": ['/data/1'],
                "paths": ['/name'],
                "data": {'name': ['Ensure this value has at most 100 ' +
                                  'characters (it has 180).']}
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertEqual(Post.objects.count(), 0)

    def test_create_models_save_error_atomic(self):
        """ Ensure models are not created if one of them raises exception."""
        response = self.client.post(
            '/api/author',
            json.dumps({
                "data": [{
                    "name": "short name"
                }, {
                    "name": "forbidden name"
                }],
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)

        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32102,
                "title": "Model form save error",
                "detail": "Name forbidden name is not allowed",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertEqual(Author.objects.count(), 0)

    def test_create_model_resource_clean_error(self):
        response = self.client.post(
            '/api/author',
            json.dumps({
                "data": {
                    "name": "not clean name"
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)
        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32100,
                "title": "Resource validation error",
                "detail": "Author name should not be 'not clean name'",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertEqual(Author.objects.count(), 0)

    def test_create_model_parse_error(self):
        response = self.client.post(
            '/api/author',
            'name=author',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)
        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32002,
                "title": "Document parse error",
                "detail": "name=author",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_create_model_invalid_request(self):
        response = self.client.post(
            '/api/author',
            json.dumps({
                "name": "author"
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)
        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32004,
                "title": "Invalid request document data key missing",
                "detail": "",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_model(self):
        author = mixer.blend("testapp.author", name="")
        response = self.client.put(
            '/api/author/{}'.format(author.id),
            json.dumps({
                "data": {
                    "id": author.id,
                    "name": "author",
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.get()
        self.assertEqual(author.name, "author")

        expected_data = {
            "data": {
                "id": author.id,
                "name": "author"
            }
        }
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_models(self):
        authors = mixer.cycle(2).blend("testapp.author", name="")
        response = self.client.put(
            '/api/author/{}'.format(",".join([str(a.id) for a in authors])),
            json.dumps({
                "data": [{
                    "id": a.id,
                    "name": "author",
                } for a in authors],
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 2)
        for author in Author.objects.all():
            self.assertEqual(author.name, "author")

        expected_data = {
            "data": [{
                "id": a.id,
                "name": "author",
            } for a in authors],
        }
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_model_missing_ids(self):
        mixer.blend("testapp.author")
        response = self.client.put(
            '/api/author',
            {
                "data": {
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

    def test_update_model_authentication(self):
        # could not update resources withour permission.
        other_user = mixer.blend(User)
        response = self.client.put(
            '/api/user/{}'.format(other_user.id),
            json.dumps({
                "data": {"id": other_user.id, "email": "email@example.com"},
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.put(
            '/api/user/{}'.format(self.user.id),
            json.dumps({
                "data": {"id": other_user.id, "email": "email@example.com"},
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            '/api/user/{}'.format(other_user.id),
            json.dumps({
                "data": {"id": self.user.id, "email": "email@example.com"},
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

        self.assertNotEqual(self.user.email, "email@example.com")
        response = self.client.put(
            '/api/user/{}'.format(self.user.id),
            json.dumps({
                "data": {"id": self.user.id, "email": "email@example.com"},
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.email, "email@example.com")

    def test_update_model_validation_error(self):
        author = mixer.blend('testapp.author')
        response = self.client.put(
            '/api/author/{}'.format(author.id),
            json.dumps({
                "data": {
                    "id": author.id,
                    "name": "a" * 101,
                },
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32101,
                "detail": "",
                "links": ['/data/0'],
                "paths": ['/name'],
                "title": "Model form validation error",
                "data": {'name': ['Ensure this value has at most 100 ' +
                                  'characters (it has 101).']},
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_models_save_error_atomic(self):
        """ Ensure models are not created if one of them raises exception."""
        authors = mixer.cycle(2).blend('testapp.author', name="name")
        response = self.client.put(
            '/api/author/{}'.format(",".join([str(a.id) for a in authors])),
            json.dumps({
                "data": [{
                    "id": authors[0].id,
                    "name": "allowed name",
                }, {
                    "id": authors[1].id,
                    "name": "forbidden name",
                }],
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)

        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32102,
                "title": "Model form save error",
                "detail": "Name forbidden name is not allowed",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)
        self.assertEqual(Author.objects.count(), 2)
        self.assertEqual(
            set(Author.objects.values_list("name", flat=True)), {'name'})

    def test_update_partial(self):
        post = mixer.blend('testapp.postwithpicture', title="title")
        response = self.client.put(
            '/api/postwithpicture/{}'.format(post.id),
            json.dumps({
                "data": [{
                    "id": post.id,
                    "title": "new title",
                }],
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 200)
        post = PostWithPicture.objects.get()
        self.assertEqual(post.title, "new title")

    def test_update_model_parse_error(self):
        author = mixer.blend("testapp.author", name="")
        response = self.client.put(
            '/api/author/{}'.format(author.id),
            'name=author',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)
        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32002,
                "title": "Document parse error",
                "detail": "name=author",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_model_invalid_request(self):
        author = mixer.blend("testapp.author", name="")
        response = self.client.put(
            '/api/author/{}'.format(author.id),
            json.dumps({
                "name": "author"
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400)
        expected_data = {
            "errors": [{
                "status": 400,
                "code": 32004,
                "title": "Invalid request document data key missing",
                "detail": "",
            }]
        }

        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_model_exclude_properties_from_form(self):
        """ Test post/put sets attributes from fieldnames_include.

        NOTE: dummy is a resource attrubute, it does not exist in model. Value
        is ignored and during result object serialization, it would be set again

        NOTE: title_uppercased is a property of parent model which is included
        in fieldnames_include of current resource. It has setter and is saved.

        """
        post = mixer.blend("testapp.postwithpicture", title="post")
        response = self.client.put(
            '/api/postwithpicture/{}'.format(post.id),
            json.dumps({
                "data": [{
                    "id": post.id,
                    "dummy": "dummy",  # dummy resource field
                    "title_uppercased": "NEW POST",
                }]
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        expected_data = {
            "data": [{
                "id": post.id,
                "picture_url": post.picture_url,
                "title_uppercased": "NEW POST",
                "dummy": "dummy",
                "links": {
                    "user": post.user and post.user.id,
                    "author": post.author and post.author.id
                }
            }]
        }
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_model_property_setter_errors(self):
        post = mixer.blend("testapp.postwithpicture", title="post")
        response = self.client.put(
            '/api/postwithpicture/{}'.format(post.id),
            json.dumps({
                "data": [{
                    "id": post.id,
                    "title_uppercased": "not uppercased title",
                }]
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        expected_data = {
            'errors': [{
                'code': 32102,
                'detail': 'Value of title_uppercased should be uppercased',
                'status': 400,
                'title': 'Model form save error'
            }]
        }
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, expected_data)

    def test_update_hidden_user_field_date_joined(self):
        date_joined = self.user.date_joined
        new_date_joined = date_joined - datetime.timedelta(days=1)
        response = self.client.put(
            '/api/user/{}'.format(self.user.id),
            json.dumps({
                "data": [{
                    "id": self.user.id,
                    "date_joined": new_date_joined.date().isoformat(),
                }]
            }),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.date_joined, date_joined)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data['data'][0]['date_joined'],
                         user.date_joined.isoformat())

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

    def test_delete_now_own_models(self):
        user = mixer.blend(User)
        response = self.client.delete(
            '/api/user/{}'.format(user.id),
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 403)
        expected_data = {
            "errors": [{
                'code': 32001,
                'detail': '',
                'status': 403,
                'title': 'Resource forbidden error',
            }]
        }
        data = json.loads(response.content.decode("utf-8"))
        compare(data, expected_data)

    def test_get_top_level_links(self):
        post = mixer.blend("testapp.post")
        response = self.client.get(
            '/api/post',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "data": [{
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

        data = json.loads(response.content.decode("utf-8"))
        compare(data, expected_data)

    def test_get_include(self):
        author = mixer.blend("testapp.author")
        mixer.cycle(2).blend("testapp.post", author=author)
        response = self.client.get(
            '/api/post?include=author',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))["linked"]
        expected_data = [{
            "type": "author",
            "id": author.id,
            "name": author.name
        }]
        self.assertEqual(data, expected_data)

    def test_get_include_null(self):
        """ Test include optional foreign key field."""
        post1 = mixer.blend("testapp.post")
        post2 = mixer.blend("testapp.post", user__username="username")
        user = post2.user

        # prefetch related join is done in python
        with self.assertNumQueries(1):
            response = self.client.get(
                '/api/post?include=user',
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        expected_data = {
            "data": [{
                "id": post.id,
                "title": post.title,
                "links": {
                    "author": post.author_id,
                    "user": post.user_id,
                }
            } for post in [post1, post2]],
            "linked": [{
                "type": "user",
                "id": user.id,
                "date_joined": user.date_joined.isoformat(),
                "email": user.email,
                'first_name': user.first_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'last_login': user.last_login and user.last_login.isoformat(),
                'last_name': user.last_name,
                'username': user.username,
            }],
            'links': {
                'posts.author': 'http://testserver/api/author/{posts.author}',
                'posts.user': 'http://testserver/api/user/{posts.user}'
            },
        }
        self.maxDiff = None
        self.assertEqual(data, expected_data)

    def test_get_include_many(self):
        comment = mixer.blend("testapp.comment")

        # prefetch related join is done in python
        with self.assertNumQueries(2):
            response = self.client.get(
                '/api/post?include=comments',
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )
        data = json.loads(response.content.decode("utf-8"))["linked"]
        expected_data = [{
            "type": "comments",
            "id": comment.id,
            "links": {
                "author": comment.author_id,
                "post": comment.post_id,
            },
        }]
        self.assertEqual(data, expected_data)

    def test_get_include_fields(self):
        mixer.blend("testapp.postwithpicture")
        response = self.client.get(
            '/api/postwithpicture',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("title_uppercased", data["data"][0])

        response = self.client.get(
            '/api/post',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertNotIn("title_uppercased", data["data"][0])

    def test_get_exclude_fields(self):
        mixer.blend("testapp.postwithpicture")
        response = self.client.get(
            '/api/postwithpicture',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertNotIn("title", data["data"][0])

    def test_get_include_many_to_many(self):
        group = mixer.blend('testapp.group')
        authors = mixer.cycle(2).blend('testapp.author')
        memberships = mixer.cycle(2).blend('testapp.membership', group=group,
                                           author=(a for a in authors))

        # prefetch related join is done in python
        with self.assertNumQueries(2):
            response = self.client.get(
                '/api/author?include=memberships',
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )

        data = json.loads(response.content.decode("utf-8"))
        expected_data = {
            "data": [{
                "id": author.id,
                "name": author.name,
                "links": {
                    "memberships": author.membership_set.values_list(
                        "id", flat=True)
                }
            } for author in authors],
            "links": {
            },
            "linked": [{
                "type": "memberships",
                "id": membership.id,
                "links": {
                    "group": membership.group_id,
                    "author": membership.author_id,
                }
            } for membership in memberships]
        }
        compare(data, expected_data)

        response = self.client.get(
            '/api/author?include=memberships,memberships.group',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        expected_data["linked"].append({
            "type": "group",
            "id": group.id,
            "name": group.name,
        })
        compare(data, expected_data)

    def test_get_include_many_many_db_queries(self):
        mixer.cycle(10).blend("testapp.comment")
        # prefetch related join is done in python twice.
        with self.assertNumQueries(3):
            self.client.get(
                '/api/author?include=posts,posts.comments',
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )

    def test_get_include_db_query(self):
        mixer.cycle(10).blend("testapp.comment")
        # prefetch related join is done in python twice.
        # TODO: add 'comments.author' relationship (->to-many->to-one).
        with self.assertNumQueries(3):
            self.client.get(
                '/api/post?include=author,comments,author.comments',
                content_type='application/vnd.api+json',
                HTTP_ACCEPT='application/vnd.api+json'
            )

    def test_get_filter_queryset(self):
        mixer.cycle(3).blend("testapp.comment")
        response = self.client.get(
            '/api/comment?filter=id__gt=1',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data['data']), 2)

    def test_get_filter_queryset_duplicated_key(self):
        mixer.cycle(3).blend("testapp.comment")
        response = self.client.get(
            '/api/comment?filter=id__gt=1&filter=id__lt=3',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data['data']), 1)

    def test_get_filter_queryset_two_fields(self):
        comments = mixer.cycle(3).blend(
            "testapp.comment",
            author__name=(x for x in ['Alice', 'Bob', 'Bill']))
        response = self.client.get(
            '/api/comment?filter=id__lt=3&filter=author__name__startswith=B',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['id'], 2)

    def test_get_filter_queryset_custom_filter(self):
        mixer.cycle(3).blend("testapp.comment")
        response = self.client.get(
            '/api/comment?filter=is_outdated=1',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data['data']), 1)

    def test_get_sort(self):
        mixer.cycle(2).blend("testapp.comment")
        response = self.client.get(
            '/api/comment?sort=-id',
            content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json'
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual([o['id'] for o in data['data']], [2, 1])
