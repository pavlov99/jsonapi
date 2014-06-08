from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from .resources import api


urlpatterns = patterns(
    '',
    url(r'^api/', include(api.urls)),
)
