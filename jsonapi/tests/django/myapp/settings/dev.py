from .base import *


INSTALLED_APPS += (
    'django_extensions',

    # If you're using Django 1.7.x or later
    # 'debug_toolbar.apps.DebugToolbarConfig',
    # If you're using Django 1.6.x or earlier
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


logging.info('Dev settings has been loaded.')
