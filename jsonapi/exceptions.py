class JSONAPIError(Exception):

    """ Exception class for JSONAPI.

    .. versionadded:: 0.6.9

    """

    def __init__(self, status_code, message=''):
        self.status_code = status_code
        self.message = message
