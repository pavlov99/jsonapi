""" JSON-API signals."""
import django.dispatch

signal_request = django.dispatch.Signal()
signal_response = django.dispatch.Signal()
