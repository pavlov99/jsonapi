.. jsonapi documentation master file, created by
   sphinx-quickstart on Mon Jun  9 10:29:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to json:api's documentation!
===================================

.. toctree::
   :maxdepth: 2

Installation
============
Requires: Django (currently tested with 1.6 only)

.. code-block:: python

    pip install jsonapi

Quickstart
==========
Create resource for model, register it with api and use it within urls!

.. code-block:: python

    # resources.py
    from jsonapi.api import API
    from jsonapi.resource import Resource

    api = API()

    @api.register
    class AuthorResource(Resource):
        class Meta:
            model = 'testapp.author'

    # urls.py
    urlpatterns = patterns(
        '',
        url(r'^api', include(api.urls))
    )


Notes
=====

REST anti patterns http://www.infoq.com/articles/rest-anti-patterns

Features
========

What makes a decent API Framework? These features:

    + \+ Pagination
    + Posting of data with validation
    + \+ Publishing of metadata along with querysets
    + \+ API discovery
    + Proper HTTP response handling
    + Caching
    + \+ Serialization
    + Throttling
    + Authentication
    + Permissions

Proper API frameworks also need:

    + Really good test coverage of their code
    + Decent performance
    + Documentation
    + An active community to advance and support the framework

TODO
====

Define logger. It could write to database of file. Data is accessable in admin interface. Format is similar to /var/log/nginx/access.log


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

