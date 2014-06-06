from django.conf import settings


def configure_settings():
    settings.configure(
        SECRET_KEY='e58!xphpu*brut!#ivn)n(%pqs6e-u6ris#+7h8q50r&wa4-uk',
        DEBUG=True,
        #TEMPLATE_DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                'USER': '',
                'PASSWORD': '',
            }
        },
        CACHE_BACKEND='locmem://',
        ROOT_URLCONF='myapp.urls',
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'myapp',
            'jsonapi',

            'django_extensions',
        ),
    )

#from django.core.management import call_command
#call_command('syncdb', interactive=False)
