"""
This module contains the class and methods for working with the database engine in the vault.
"""
from typing import Union
from logger import log

import hvac
import hvac.exceptions

from .exceptions import WrongDBConfiguration


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class DBEngine:
    """
    This class is responsible for working with the database engine in the vault.
    Supported methods for:
        - generate credentials
    """
    def __init__(
        self,
        client: hvac.Client = None,
        connection_name: str = None,
        connection_url: str = None,
        mount_point: str = None,
        **kwargs
    ) -> None:
        """
        A method for creating an instance of the database engine.

        Args:
            :param client (hvac.Client): client instance with a connection to the vault
            :param connection_name (str): database connection name
            :param connection_url (str): database connection url, example `postgresql://{{{{username}}}}:{{{{password}}}}@postgres:5432/postgres?sslmode=disable`
            :param mount_point (str): database engine mount point

        Keyword Args:
            :param plugin_name (str): database plugin name (default 'postgresql-database-plugin')
            :param allowed_roles (list): database roles allowed to access the database (default same as `connection_name`)
            :param username (str): database username, default `postgres`
            :param password (str): database password, default `postgres`

        Returns:
            None

        Examples:
            >>> from vault import DBEngine
            >>> from hvac import Client
            >>> client = Client()
            >>> db_engine = DBEngine(
            ...     client=client,
            ...     connection_name='postgresql',
            ...     connection_url='postgresql://{{username}}:{{password}}@postgres:5432/postgres?sslmode=disable',
            ...     mount_point='database',
            ...     plugin_name='postgresql-database-plugin',
            ...     allowed_roles=['readonly', 'readwrite'],
            ...     username='postgres',
            ...     password='postgres'
            ... )
        """
        log.info('[VaultClient] configuration database engine for client %s', client)

        self.client = client
        self.connection_name = connection_name
        self.connection_url = connection_url
        self.mount_point = mount_point
        self.plugin_name = kwargs.get('plugin_name', 'postgresql-database-plugin')
        self.allowed_roles = kwargs.get('allowed_roles', list[connection_name])
        self.username = kwargs.get('username', 'postgres')
        self.password = kwargs.get('password', 'postgres')

        if self.client and self.connection_name and self.connection_url and self.mount_point:
            self.client.secrets.database.configure(
                name=self.connection_name,
                plugin_name=self.plugin_name,
                allowed_roles=self.allowed_roles,
                connection_url=self.connection_url,
                username=self.username,
                password=self.password
            )
            log.info('[VaultClient] database engine configured successfully', client)
        else:
            raise WrongDBConfiguration('Incorrect database engine configuration. Check the required parameters.')

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
            response = self.client.secrets.database.generate_credentials(
                name=role,
                mount_point=self.mount_point
            )
            log.info('[VaultClient] generated database credentials for role %s', self.client, role)
            return response['data']
        except hvac.exceptions.InvalidPath:
            log.error('[VaultClient] database role %s does not exist', self.client, role)
            return None
