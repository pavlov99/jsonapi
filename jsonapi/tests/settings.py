SECRET_KEY = 'e58!xphpu*brut!#ivn)n(%pqs6e-u6ris#+7h8q50r&wa4-uk'

DEBUG = True
#TEMPLATE_DEBUG=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
    }
}
#CACHES = {
    #'default': {
        #'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    #}
#}

ROOT_URLCONF = 'myapp.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'jsonapi',
)

#MIDDLEWARE_CLASSES = (
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
#)
