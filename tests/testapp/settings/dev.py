from .test import *

INSTALLED_APPS += (
    # If you're using Django 1.7.x or later
    # 'debug_toolbar.apps.DebugToolbarConfig',
    # If you're using Django 1.6.x or earlier
    'debug_toolbar',
    'django_extensions',

)
DATABASES['default']['NAME'] = 'db.sqlite3'
STATIC_URL = '/static/'
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Allow to use debug toolbar with json response
    'tests.testapp.middleware.NonHtmlDebugToolbarMiddleware',
)
INTERNAL_IPS = [
    '127.0.0.1',
    '33.33.33.1',
]
