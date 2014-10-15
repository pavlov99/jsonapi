from django.http import HttpResponse
from django.conf import settings
import json


class NonHtmlDebugToolbarMiddleware(object):

    """ The Django Debug Toolbar usually only works for views that return HTML.

    This middleware wraps any non-HTML response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)
    Special handling for json (pretty printing) and
    binary data (only show data length).

    """

    @staticmethod
    def process_response(request, response):
        if settings.DEBUG:
            if response['Content-Type'] != 'text/html':
                content = response.content.decode('utf8')
                try:
                    json_ = json.loads(content)
                    content = json.dumps(json_, sort_keys=True, indent=2)
                except ValueError:
                    pass
                response = HttpResponse(
                    '<html><body><pre>{}</pre></body></html>'.format(content)
                )

        return response
