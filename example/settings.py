SECRET_KEY = "^rbf8k&st!yclg!))2+n_fxp4@oou&$nnjz8*tfx!mrjzj*q%d"
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sessions',
    'testapp',
    'jsonapi',

    # If you're using Django 1.7.x or later
    # 'debug_toolbar.apps.DebugToolbarConfig',
    # If you're using Django 1.6.x or earlier
    'debug_toolbar',
    'django_extensions',
]
# Django replaces this, but it still wants it. *shrugs*
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
ROOT_URLCONF = 'testapp.urls'
STATIC_URL = '/static/'
DEBUG = True
TEMPLATE_DEBUG = True
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Allow to use debug toolbar with json response
    'testapp.middleware.NonHtmlDebugToolbarMiddleware',
)
INTERNAL_IPS = [
    '127.0.0.1',
    '33.33.33.1',
]
