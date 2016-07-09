JSON-API
========

.. image:: https://travis-ci.org/pavlov99/jsonapi.png
    :target: https://travis-ci.org/pavlov99/jsonapi
    :alt: Build Status

.. image:: https://coveralls.io/repos/pavlov99/jsonapi/badge.png
    :target: https://coveralls.io/r/pavlov99/jsonapi
    :alt: Coverage Status

.. image:: https://pypip.in/v/jsonapi/badge.png
    :target: https://crate.io/packages/jsonapi
    :alt: Version

.. image:: https://pypip.in/download/jsonapi/badge.svg
    :target: https://pypi.python.org/pypi/jsonapi/
    :alt: Downloads

.. image:: https://pypip.in/format/jsonapi/badge.png
    :target: https://pypi.python.org/pypi/jsonapi/
    :alt: Download format

.. image:: https://pypip.in/license/jsonapi/badge.png
    :target: https://pypi.python.org/pypi/jsonapi/
    :alt: License

.. image:: https://pypip.in/status/jsonapi/badge.svg
    :target: https://pypi.python.org/pypi/jsonapi/
    :alt: Development Status


Django module with json-api standard support.
It lets you easily add powerful api on top of your models and generate auto documentation.
Module is focused on simple integration allowing developers to add features later on.
Most of the functions would work out of the box.

Compared to other solutions, this project does Django model introspection.
It allows to automatically query database using select_related/prefetch_related options for related resources.
No more configs, if you would like to include one resource into another, you are able to do that from client side.
Your client knows, when it needs it. Server in this case would perform db queries in a most efficient way.

Development
===========

.. image:: https://badge.waffle.io/pavlov99/jsonapi.png?label=ready&title=Ready
    :target: https://waffle.io/pavlov99/jsonapi/
    :alt: Ready stories.

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/pavlov99/jsonapi
   :target: https://gitter.im/pavlov99/jsonapi?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


Throughput Graph
----------------

.. image:: https://graphs.waffle.io/pavlov99/jsonapi/throughput.svg
    :target: https://waffle.io/pavlov99/jsonapi/metrics
    :alt: 'Throughput Graph'


Documentation
=============

Library: http://jsonapi.readthedocs.org/

Api Specification: http://jsonapi.org/

TODO
====

I'm going to migrate backend ORM to peewee soon. During development I would support Django all the time.
Idea behind it is to unify framework, so it would be possible to use jsonapi with Tornado, Flask or Asyncio.
