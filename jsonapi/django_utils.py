""" Django specific utils.

Utils are used to work with different django versions.

"""
import django
from django.db import models
from django.http import QueryDict
from . import six


def get_model_by_name(model_name):
    """ Get model by its name.

    :param str model_name: name of model.
    :return django.db.models.Model:

    Example:
        get_concrete_model_by_name('auth.User')
        django.contrib.auth.models.User

    """
    if isinstance(model_name, six.string_types) and \
            len(model_name.split('.')) == 2:
        app_name, model_name = model_name.split('.')

        if django.VERSION[:2] < (1, 8):
            model = models.get_model(app_name, model_name)
        else:
            from django.apps import apps
            model = apps.get_model(app_name, model_name)
    else:
        raise ValueError("{0} is not a Django model".format(model_name))

    return model


def get_model_name(model):
    """ Get model name for the field.

    Django 1.5 uses module_name, does not support model_name
    Django 1.6 uses module_name and model_name
    DJango 1.7 uses model_name, module_name raises RemovedInDjango18Warning

    """
    opts = model._meta
    if django.VERSION[:2] < (1, 7):
        model_name = opts.module_name
    else:
        model_name = opts.model_name

    return model_name


def clear_app_cache(app_name):
    """ Clear django cache for models.

    :param str ap_name: name of application to clear model cache

    """
    loading_cache = django.db.models.loading.cache

    if django.VERSION[:2] < (1, 7):
        loading_cache.app_models[app_name].clear()
    else:
        loading_cache.all_models[app_name].clear()


def get_querydict(query):
    if six.PY2:
        return dict(QueryDict(query).iterlists())
    else:
        return dict(QueryDict(query).lists())


def get_models():
    if django.VERSION[:2] < (1, 8):
        return models.get_models()
    else:
        from django.apps import apps
        return apps.get_models()
