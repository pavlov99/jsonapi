from django.test import TestCase
from ..resources import UserResource


class TestResource(TestCase):
    def test_get_form(self):
        # Return defined in Meta forms
        self.assertEqual(UserResource.get_form(), UserResource.Meta.form)

    def test_get_partial_form(self):
        Form = UserResource.get_partial_form(UserResource.get_form(), None)
        self.assertEqual(Form, UserResource.get_form())
        self.assertNotIn("date_joined", Form.base_fields)

        Form = UserResource.get_partial_form(
            UserResource.get_form(), ["date_joined"])
        # Fields could only be excluded.
        self.assertNotIn("date_joined", Form.base_fields)
