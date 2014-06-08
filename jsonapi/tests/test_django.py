""" Prepare a Django project for tests. """
from django.conf import settings


settings.configure(
    SECRET_KEY='e58!xphpu*brut!#ivn)n(%pqs6e-u6ris#+7h8q50r&wa4-uk',
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'USER': '',
            'PASSWORD': '',
        }
    },
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    ROOT_URLCONF='myapp.urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'myapp',
        #'jsonapi',
    ),
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
)

from django.core.management import call_command
call_command('syncdb', interactive=False)

#from .django.myapp.tests   import *
