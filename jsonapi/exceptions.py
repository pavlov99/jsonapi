import json

from . import statuses


class JSONAPIError(Exception):

    """ Exception class for JSONAPI.

    .. versionadded:: 0.6.9
    .. versionchanged:: 0.8.4
      Use JSON-API Specification http://jsonapi.org/format/#errors

    Error codes are from 0 to 32767.
    Error codes 32000 - 32767 are reserved fro jsonapi usage.
    It is recommended for user to use codes from 0 to 32000, in this case codes
    could be stored within django.PositiveSmallIntegerField field

    """

    ATTRIBUTES = [
        "id",
        "href",
        "status",
        "code",
        "title",
        "detail",
        "links",
        "paths",
    ]

    REQUIRED_ATTRIBUTES = ["code", "title"]

    def __init__(self, **kwargs):
        kwargs["code"] = getattr(self, 'CODE', kwargs["code"])
        kwargs["title"] = getattr(self, 'TITLE', kwargs["title"])
        kwargs["status"] = getattr(self, 'STATUS', kwargs["status"])

        for required_attribut in self.REQUIRED_ATTRIBUTES:
            if required_attribut not in kwargs:
                raise ValueError("{} should have {} attribute".format(
                    self.__class__.__name__, required_attribut
                ))

        for kwarg_key, kwarg_value in kwargs.items():
            if kwarg_key not in self.ATTRIBUTES:
                raise ValueError(
                    "Attribute {} is not allowed".format(kwarg_key))

        self.data = kwargs

    def __str__(self):
        return json.dumps(self.data)


class JSONAPIResourceValidationError(JSONAPIError):
    """ Error raised during resource validation."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32100
    TITLE = "Resource Validation Error"


class JSONAPIFormValidationError(JSONAPIError):
    """ Error raised during Django form validation."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32101
    TITLE = "Model Form Validation Error"


class JSONAPIFormSaveError(JSONAPIError):
    """ Resource form save error."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32102
    TITLE = "Model Form Validation Error"


class JSONAPIIntegrityError(JSONAPIError):
    """ Database error on form save."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32103
    TITLE = "Database Ialidation Error"
