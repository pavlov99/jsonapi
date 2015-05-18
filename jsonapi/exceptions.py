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
        "data",
    ]

    REQUIRED_ATTRIBUTES = ["code", "title"]
    CODE = 32000
    STATUS = statuses.HTTP_400_BAD_REQUEST
    TITLE = "General JSONAPI Error"

    def __init__(self, **kwargs):
        kwargs["code"] = self.CODE
        kwargs["title"] = self.TITLE
        kwargs["status"] = self.STATUS
        kwargs["detail"] = kwargs.get("detail", "")

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

    def __getattr__(self, key):
        if key == "data":
            return self.data
        else:
            return self.data[key]


class JSONAPIForbiddenError(JSONAPIError):
    """ Resource Access of Manipulation forbidden."""

    STATUS = statuses.HTTP_403_FORBIDDEN
    CODE = 32001
    TITLE = "Resource forbidden error"


class JSONAPIParseError(JSONAPIError):
    """ Error raised during request parsing."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32002
    TITLE = "Document parse error"


class JSONAPIInvalidRequestError(JSONAPIError):
    """ Error raised during requested document cleanup."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32003
    TITLE = "Invalid request"


class JSONAPIInvalidRequestDataMissingError(JSONAPIError):
    """ Requested document does not have data key."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32004
    TITLE = "Invalid request document data key missing"


class JSONAPIResourceValidationError(JSONAPIError):
    """ Error raised during resource validation."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32100
    TITLE = "Resource validation error"


class JSONAPIFormValidationError(JSONAPIError):
    """ Error raised during Django form validation."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32101
    TITLE = "Model form validation error"


class JSONAPIFormSaveError(JSONAPIError):
    """ Resource form save error."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32102
    TITLE = "Model form save error"


class JSONAPIIntegrityError(JSONAPIError):
    """ Database integrity error on form save."""

    STATUS = statuses.HTTP_400_BAD_REQUEST
    CODE = 32103
    TITLE = "Database integrity error"
