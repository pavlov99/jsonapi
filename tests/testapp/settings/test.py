import os.path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)

SECRET_KEY = "^rbf8k&st!yclg!))2+n_fxp4@oou&$nnjz8*tfx!mrjzj*q%d"
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sessions',
    'tests.testapp',
)
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
ROOT_URLCONF = 'tests.testapp.urls'
DEBUG = True
TEMPLATE_DEBUG = True
