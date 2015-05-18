from django.dispatch import receiver
from jsonapi.signals import (
    signal_request as jsonapi_signal_request,
    signal_response as jsonapi_signal_response,
)

import logging

logger = logging.getLogger(__name__)


@receiver(jsonapi_signal_request)
def log_jsonapi_request(sender, signal, request=None):
    msg = "{} {}".format(request.method, request.get_full_path())
    msg = "{method} {path}".format(
        method=request.method, path=request.get_full_path())
    logger.info(msg)


@receiver(jsonapi_signal_response)
def log_jsonapi_response(sender, signal, request=None,
                         response=None, duration=None):
    msg = "{method} {path}".format(
        method=request.method,
        path=request.get_full_path()
    )
    if request.body:
        msg += " --data '{}'".format(request.body.decode('utf8'))

    msg += "; status={status_code} ({duration:.3f} sec)".format(
        duration=duration,
        status_code=response.status_code
    )
    logger.info(msg)
