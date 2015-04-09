JSONAPI Resource
================

Resources are related to Django models.
Basic customization is done in Resource.Meta class.
Exampele of resource declaration is shown below:

.. code-block:: python

    from jsonapi.api import API
    from jsonapi.resource import Resource
    from django.conf import settings

    api = API()

    @api.register
    class UserResource(Resource):
        class Meta:
            model = settings.AUTH_USER_MODEL
            authenticators = [Resource.AUTHENTICATORS.SESSION]
            fieldnames_exclude = 'password',


    @api.register
    class AuthorResource(Resource):
        class Meta:
            model = 'testapp.Author'
            allowed_methods = 'GET', 'POST', 'PUT', 'DELETE'


    @api.register
    class PostWithPictureResource(Resource):
        class Meta:
            model = 'testapp.PostWithPicture'
            fieldnames_include = 'title_uppercased',
            page_size = 3

    @staticmethod
    def dump_document_title(obj):
        return obj.title


Available Meta parameters:

+--------------------+---------------------------+-----------------------+-----------------------------------+
| Name               | Type                      | Default               | Usage                             |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| model              | str                       | None. Need to specify | '<appname>.<modelname>'           |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| allowed_methods    | tuple                     | ('GET')               | tuple of capitalized HTTP methods |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| authenticators     | list                      | []                    | [Resource.AUTHENTICATORS.SESSION] |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| fieldnames_include | list                      | []                    | list of field names               |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| fieldnames_exclude | list                      | []                    | list of field names               |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| page_size          | int                       | None                  | integer if need pagination        |
+--------------------+---------------------------+-----------------------+-----------------------------------+
| form               | django.forms.Form Default | ModelForm             | form to use                       |
+--------------------+---------------------------+-----------------------+-----------------------------------+

GET/POST/PUT/DELETE method kwargs
---------------------------------

+---------+--------------------------------+
| name    | note                           |
+---------+--------------------------------+
| request | Django request                 |
+---------+--------------------------------+
| ids     | ids in request url, optional   |
+---------+--------------------------------+

Exceptions
----------

+-------+--------+-----------------------------+--------------------------------+
| Code  | Status | Title                       | Class                          |
+-------+--------+-----------------------------+--------------------------------+
| 32000 | 400    | General JSONAPI Error       | JSONAPIError                   |
+-------+--------+-----------------------------+--------------------------------+
| 32001 | 403    | Resource Forbidden Error    | JSONAPIForbiddenError          |
+-------+--------+-----------------------------+--------------------------------+
| 32100 | 400    | Resource Validation Error   | JSONAPIResourceValidationError |
+-------+--------+-----------------------------+--------------------------------+
| 32101 | 400    | Model Form Validation Error | JSONAPIFormValidationError     |
+-------+--------+-----------------------------+--------------------------------+
| 32102 | 400    | Model Form Save Error       | JSONAPIFormSaveError           |
+-------+--------+-----------------------------+--------------------------------+
| 32103 | 400    | Database Integrity Error    | JSONAPIIntegrityError          |
+-------+--------+-----------------------------+--------------------------------+
