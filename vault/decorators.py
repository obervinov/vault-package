"""This module contains decorators for the VaultClient class"""
from logger import log
import hvac
import hvac.exceptions


def reauthenticate_on_forbidden(method):
    """
    Decorator for re-authenticate in the vault server when a Forbidden exception is caught.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except hvac.exceptions.Forbidden:
            log.warning('[VaultClient]: Forbidden exception caught, re-authenticating...')
            self.client = self.authentication()
            return method(self, *args, **kwargs)
    return wrapper


def deprecated_method(method):
    """
    Decorator for deprecated methods.
    """
    def wrapper(*args, **kwargs):
        log.warning(
            '[VaultClient]: method is deprecated and will be removed in the next major release, please use another method.'
            'More information at https://github.com/obervinov/vault-package/blob/v2.1.0/DEPRECATED.md',
            method.__name__
        )
        return method(*args, **kwargs)
    return wrapper
