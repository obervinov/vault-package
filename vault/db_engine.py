"""
This module contains the class and methods for working with the database engine in the vault.
"""
from typing import Union
from logger import log

import hvac
import hvac.exceptions

from .exceptions import WrongDBConfiguration
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
        vault_client: object = None,
        connection: dict = None
    ) -> None:
        """
        A method for creating an instance of the database engine.

        Args:
            :param vault_client (object): vault client instance with VaultClient class and attribute hvac.Client
            :param connection (dict): dictionary with database connection configuration.
                :param name (str): database connection name
                :param url (str): database connection url, example `postgresql://{{{{username}}}}:{{{{password}}}}@postgres:5432/postgres?sslmode=disable`
                :param mount_point (str): database engine mount point
                :param plugin_name (str): database plugin name (default 'postgresql-database-plugin')
                :param allowed_roles (list): database roles allowed to access the database (default same as `connection_name`)
                :param username (str): database username, default `postgres`
                :param password (str): database password, default `postgres`

        Returns:
            None

        Examples:
            >>> from vault import DBEngine, VaultClient
            >>> client = VaultClient(url='http://localhost:8200', namespace='test')
            >>> db_engine = DBEngine(
            ...     vault_client=client,
            ...     connection={
            ...         'name': 'mydb',
            ...         'url': 'postgresql',
            ...         'mount_point': 'database',
            ...         'plugin_name': 'postgresql-database-plugin',
            ...         'allowed_roles': ['readonly', 'readwrite'],
            ...         'username': 'postgres',
            ...         'password': 'postgres'
            ...     }
            ... )
        """
        log.info('[VaultClient] configuration database engine for client %s', vault_client.client)

        self.client = vault_client.client
        self.vault_client = vault_client
        self.connection = connection

        # Check required keys in connection dictionary
        if not all(key in self.connection for key in ['name', 'url', 'username', 'password']):
            raise WrongDBConfiguration('Incorrect database engine configuration. Check the required parameters.')

        # Set default parameters if don't exist
        self.connection['mount_point'] = self.connection.get('mount_point', self.vault_client.namespace)
        self.connection['plugin_name'] = self.connection.get('plugin_name', 'postgresql-database-plugin')
        self.connection['allowed_roles'] = self.connection.get('allowed_roles', [self.vault_client.namespace])

        self.client.secrets.database.configure(
            name=self.connection['name'],
            plugin_name=self.connection['plugin_name'],
            allowed_roles=self.connection['allowed_roles'],
            connection_url=self.connection['url'],
            username=self.connection['username'],
            password=self.connection['password']
        )
        log.info('[VaultClient] database engine configured successfully: %s', self.client)

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
            response = self.client.secrets.database.generate_credentials(name=role, mount_point=self.connection['mount_point'])
            log.info('[VaultClient] generated database credentials for role %s', role)
            return response['data']
        except hvac.exceptions.InvalidPath:
            log.error('[VaultClient] database role %s does not exist', role)
            return None
