"""This module contains the class and methods for working with the kv v2 engine in the vault"""
from typing import Union
from logger import log

import hvac
import hvac.exceptions

from .exceptions import WrongKV2Configuration
from .decorators import reauthenticate_on_forbidden


class KV2Engine:
    """
    This class is responsible for working with the kv v2 engine in the vault.
    Supported methods for:
        - read secret
        - create or update secret
        - list secrets
        - delete secret
    """
    def __init__(
        self,
        vault_client: object = None,
        **kwargs
    ) -> None:
        """
        A method for creating an instance of the kv v2 engine.

        Args:
            :param vault_client (object): vault client instance with VaultClient class and attribute hvac.Client

        Keyword Args:
            :param max_versions (int): maximum number of versions of the secret available for storage (default 10)
            :param cas_required (bool): all keys will require the cas parameter to be set on all write requests (default False)
            :param raise_on_deleted_version (bool): changes the behavior when the requested version is deleted (default True)
                if True an exception will be raised
                if False, some metadata about the deleted secret is returned
                if None (pre-v3), a default of True will be used and a warning will be issued

        Returns:
            None

        Examples:
            >>> from vault import KV2Engine, VaultClient
            >>> client = VaultClient(url='http://localhost:8200', namespace='test')
            >>> kv2 = KV2Engine(
            ...     vault_client=client,
            ...     mount_point='secret',
            ...     max_versions=10,
            ...     cas_required=False,
            ...     raise_on_deleted_version=True
            ... )
        """
        log.info('[VaultClient] configuration KV2 Engine for client %s', vault_client.client)

        self.client = vault_client.client
        self.vault_client = vault_client
        self.max_versions = kwargs.get('max_versions', 10)
        self.mount_point = vault_client.namespace
        self.cas_required = kwargs.get('cas_required', False)
        self.raise_on_deleted_version = kwargs.get('raise_on_deleted_version', True)

        if self.mount_point and self.client:
            self.client.secrets.kv.v2.configure(
                max_versions=self.max_versions,
                mount_point=self.mount_point,
                cas_required=self.cas_required
            )
            log.info('[VaultClient] configuration KV2 Engine for client %s has been completed', self.client)
        else:
            raise WrongKV2Configuration("Mount point not specified, KV2 Engine configuration error. Please set the argument mount_point=<mount_point_name>.")

    @reauthenticate_on_forbidden
    def read_secret(
        self,
        path: str = None,
        key: str = None
    ) -> Union[str, dict, None]:
        """
        A method for read secret from KV2 Engine.

        Args:
            :param path (str): the path to the secret in vault.
            :param key (str): specify the key if you want to get only the value of a specific key.

        Returns:
            (str) 'value'
                or
            (dict) {'key': 'value'}
                or
            None
        """
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point,
                raise_on_deleted_version=self.raise_on_deleted_version
            )
            if key:
                return response['data']['data'][key]
            return response['data']['data']
        except hvac.exceptions.InvalidPath as invalid_path:
            log.warning('[VaultClient] the path %s/%s does not exist: %s', path, key, invalid_path)
            return None

    @reauthenticate_on_forbidden
    def write_secret(
        self,
        path: str = None,
        key: str = None,
        value: str = None
    ) -> object:
        """
        A method for create or update secret in KV2 Engine.

        Args:
            :param path (str): the path to the secret in vault.
            :param key (str): the key to write to the secret.
            :param value (str): the value of the key to write to the secret.

        Returns:
            (object) https://www.w3schools.com/python/ref_requests_response.asp
        """
        # This is not an optimal solution,
        # but the hvac module cannot verify the existence of a secret without exception
        # https://github.com/hvac/hvac/issues/381
        try:
            # secret existence verification
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point,
                raise_on_deleted_version=self.raise_on_deleted_version
            )['data']['data']
            secret[key] = value
            # update an existing secret
            return self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret,
                mount_point=self.mount_point
            )
        except hvac.exceptions.InvalidPath:
            # if the secret doesn't exist
            return self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={key: value},
                mount_point=self.mount_point
            )

    @reauthenticate_on_forbidden
    def list_secrets(
        self,
        path: str = None
    ) -> list:
        """
        A method for list secrets from KV2 Engine.

        Args:
            :param path (str): the path to the secret in vault.

        Returns:
            (list) ['key1','key2','key3']
                or
            (list) []
        """
        try:
            return self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_point
            )['data']['keys']
        except hvac.exceptions.InvalidPath as invalid_path:
            log.error('[VaultClient] the path %s does not exist: %s', path, invalid_path)
            return []

    @reauthenticate_on_forbidden
    def delete_secret(
        self,
        path: str = None
    ) -> bool:
        """
        A method for delete secret from KV2 Engine.

        Args:
            :param path (str): the path to the secret in vault.

        Returns:
            (bool) True
                or
            (bool) False
        """
        try:
            response = self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self.mount_point
            )
            if response.status_code == 204:
                log.info('[VaultClient] the secret %s has been deleted: %s', path, response)
                return True
            log.error("[VaultClient] failed to delete secret %s: %s", path, response)
            return False
        except hvac.exceptions.InvalidPath as invalid_path:
            log.error('[VaultClient] it looks like the path %s does not exist: %s', path, invalid_path)
            return False
