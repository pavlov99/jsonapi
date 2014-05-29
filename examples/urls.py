from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from myapp.api import api


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url('^api/', include(api.urls)),
)
