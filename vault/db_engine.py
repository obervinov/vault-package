"""
This module contains the class and methods for working with the database engine in the vault.
"""
from typing import Union
from logger import log

import hvac
import hvac.exceptions

from .decorators import reauthenticate_on_forbidden


# pylint: disable=too-few-public-methods
class DBEngine:
    """
    This class is responsible for working with the database engine in the vault.
    Supported methods for:
        - generate credentials
    """
    def __init__(
        self,
        vault_client: object = None
    ) -> None:
        """
        A method for creating an instance of the database engine.

        Args:
            :param vault_client (object): vault client instance with VaultClient class and attribute hvac.Client

        Returns:
            None

        Examples:
            >>> from vault import DBEngine, VaultClient
            >>> client = VaultClient(url='http://localhost:8200', namespace='test')
            >>> db_engine = DBEngine(vault_client=client)
        """
        log.info('[VaultClient] configuration database engine for client %s', vault_client.client)
        self.client = vault_client.client
        self.vault_client = vault_client

    @reauthenticate_on_forbidden
    def generate_credentials(
        self,
        role: str
    ) -> Union[dict, None]:
        """
        A method for generating database credentials.

        Args:
            :param role (str): database role

        Returns:
            dict: database credentials

        Examples:
            >>> credentials = db_engine.generate_credentials(role='readonly')
        """
        try:
            response = self.client.secrets.database.generate_credentials(name=role, mount_point=self.vault_client.namespace)
            log.info('[VaultClient] generated database credentials for role %s', role)
            return response['data']
        except hvac.exceptions.InvalidPath:
            log.error('[VaultClient] database role %s does not exist', role)
            return None
