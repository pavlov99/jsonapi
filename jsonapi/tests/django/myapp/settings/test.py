from .base import *


DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = ':memory:'
CACHES['default']['BACKEND'] = 'django.core.cache.backends.locmem.LocMemCache'


logging.info('Test settings has been loaded.')
