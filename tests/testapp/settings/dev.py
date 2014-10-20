from .base import *

INSTALLED_APPS += (
    'django_extensions',
)

if django.VERSION[:2] < (1, 7):
    INSTALLED_APPS += 'debug_toolbar',
else:
    INSTALLED_APPS += 'debug_toolbar.apps.DebugToolbarConfig'

DATABASES['default']['NAME'] = 'db.sqlite3'
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Allow to use debug toolbar with json response
    # 'tests.testapp.middleware.NonHtmlDebugToolbarMiddleware',
)
INTERNAL_IPS = [
    '127.0.0.1',
    '33.33.33.1',
]
