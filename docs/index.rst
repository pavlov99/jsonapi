.. jsonapi documentation master file, created by
   sphinx-quickstart on Mon Jun  9 10:29:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to json:api's documentation!
====================================

.. toctree::
   :maxdepth: 3

   modules.rst

Installation
============
Requires: Django (1.5, 1.6); python (2.7, 3.3).

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
    from .resources import api

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
    + \+ Authentication
    + Authorization/Permissions

Proper API frameworks also need:

    + Really good test coverage of their code
    + Decent performance
    + Documentation
    + An active community to advance and support the framework


Docs
====

    - Resource definition
    - Resource and Models discovery
    - Authentication
    - Authorization

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

