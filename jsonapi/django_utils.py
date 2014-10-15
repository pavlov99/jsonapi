""" Django specific utils.

Utils are used to work with different django versions.

"""
import django


def get_model_name(model):
    """ Get model name for the field.

    Django 1.5 uses module_name, does not support model_name
    Django 1.6 uses module_name and model_name
    DJango 1.7 uses model_name

    """
    opts = model._meta
    return opts.module_name
