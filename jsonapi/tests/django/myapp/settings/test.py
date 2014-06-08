from .base import *


DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = ':memory:'
CACHES['default']['BACKEND'] = 'django.core.cache.backends.locmem.LocMemCache'

INSTALLED_APPS += (
    'django_nose',
)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=jsonapi',
]


logging.info('Test settings has been loaded.')
