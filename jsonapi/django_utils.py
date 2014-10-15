""" Django specific utils.

Utils are used to work with different django versions.

"""
import django


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
