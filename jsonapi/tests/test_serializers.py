from django.test import TestCase
from mixer.backend.django import mixer

from jsonapi.serializers import Serializer


class TestSerializers(TestCase):
    def test_get_id(self):
        author = mixer.blend('testapp.author')
        self.assertEqual(author.pk, Serializer.get_id(author))

    def test_get_id_inheritance(self):
        post = mixer.blend('testapp.postwithpicture')
        self.assertEqual(post.pk, Serializer.get_id(post))
