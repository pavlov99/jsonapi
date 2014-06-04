from django.conf import settings


settings.configure(
    DEBUG=True,
    TEMPLATE_DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'USER': '',
            'PASSWORD': '',
        }
    },
    CACHE_BACKEND='locmem://',
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ),
)

#from django.core.management import call_command
#call_command('syncdb', interactive=False)
