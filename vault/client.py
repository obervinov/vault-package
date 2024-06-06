"""
This module contains an implementation over the hvac module for interacting with the Vault Engines.
"""
import os

import hvac
import hvac.exceptions
from hvac.api.auth_methods import Kubernetes

from logger import log
from .kv2_engine import KV2Engine
from .db_engine import DBEngine


# pylint: disable=too-few-public-methods
class VaultClient:
    """
    This class contains classes and methods for working with Vault Engines:
    - kv v2 engine
    - database engine
    """
    def __init__(
        self,
        url: str = None,
        namespace: str = None,
        auth: dict = None,
        **kwargs
    ) -> None:
        """
        A method for create a new Vault Client instance.

        Args:
            :param url (str): base URL for the Vault instance.
            :param namespace (str): the name of the namespace in the Vault instance.
            :param auth (dict): dictionary with authentication data.
                :param type (str): type of authentication. Supported values: 'approle', 'token', 'kubernetes'.
                :param token (str): token for authentication.
                :param approle (dict): dictionary with approle credentials.
                    :param id (str): approle-id to receive a token.
                    :param secret-id (str): secret-id to receive a token.
                :param kubernetes (str): path to the kubernetes service account token.

        Keyword Args:
            :param kv2engine (dict): dictionary with kv2 engine configuration.
                :param cas_required (bool): all keys will require the cas parameter to be set on all write requests
                :param max_versions (int): maximum number of versions of the secret available for storage
                :param raise_on_deleted_version (bool): changes the behavior when the requested version is deleted
            :param dbengine (dict): dictionary with database engine configuration.
                :param connection_name (str): database connection name
                :param connection_url (str): database connection url
                :param plugin_name (str): database plugin name
                :param allowed_roles (list): database roles allowed to access the database
                :param username (str): database username
                :param password (str): database password

        Environment Variables:
            VAULT_ADDR: URL of the vault server.
            VAULT_NAMESPACE: Namespace in the vault server.
            VAULT_AUTH_TYPE: Type of authentication in the vault server. Supported values: 'approle', 'token', 'kubernetes'.
            VAULT_TOKEN: Root token with full access rights.
            VAULT_APPROLE_ID: Approle ID for authentication in the vault server.
            VAULT_APPROLE_SECRET_ID: Approle Secret ID for authentication in the vault server.
            VAULT_KUBERNETES_SA_TOKEN: Path to the kubernetes service account token.

        Returns:
            None

        Examples:
            >>> from vault import VaultClient
            >>> vault_client = VaultClient(
            ...     url='http://vault:8200',
            ...     namespace='test',
            ...     auth={
            ...         'type': 'approle',
            ...         'approle': {
            ...             'id': 'approle_id',
            ...             'secret': 'approle_secret_id'
            ...         }
            ...     },
            ...     kv2engine={
            ...         'cas_required': True,
            ...         'max_versions': 10,
            ...         'raise_on_deleted_version': False
            ...     },
            ...     dbengine={
            ...         'connection_name': 'test',
            ...         'connection_url': 'postgresql://{username}:{password}@postgres:5432/postgres?sslmode=disable',
            ...         'plugin_name': 'postgresql-database-plugin',
            ...         'allowed_roles': ['readonly', 'readwrite'],
            ...         'username': 'postgres',
            ...         'password': 'postgres'
            ...     }
            >>> secret_data = vault_client.kv2engine.read_secret(path='path/to/secret')
            >>> pg_credentials = vault_client.dbengine.generate_credentials(role='readonly')
        """
        try:
            log.info('[VaultClient]: extracting the configuration for the vault client...')
            if url:
                self.url = url
            else:
                self.url = os.environ.get('VAULT_ADDR')

            if namespace:
                self.namespace = namespace
            else:
                self.namespace = os.environ.get('VAULT_NAMESPACE')

            if auth:
                self.auth = auth
            else:
                self.auth = {'type': os.environ.get('VAULT_AUTH_TYPE')}
                if self.auth['type'] == 'approle':
                    self.auth['approle'] = {'id': os.environ.get('VAULT_APPROLE_ID'), 'secret-id': os.environ.get('VAULT_APPROLE_SECRET_ID')}
                elif self.auth['type'] == 'token':
                    self.auth['token'] = os.environ.get('VAULT_TOKEN')
                elif self.auth['type'] == 'kubernetes':
                    self.auth['kubernetes'] = os.environ.get('VAULT_KUBERNETES_SA_TOKEN', '/var/run/secrets/kubernetes.io/serviceaccount/token')
            log.info('[VaultClient]: configuration has been successfully extracted: auth: %s, url: %s, namespace: %s', self.auth['type'], self.url, self.namespace)
        except KeyError as keyerror:
            raise KeyError(
                "Failed to extract the value of the environment variable. "
                "You need to set an environment variable or pass an argument when creating an instance of VaultClient(arg=value)"
            ) from keyerror

        try:
            log.info('[VaultClient]: preparing the client for the vault server...')
            self.client = self.authentication()
            self.kv2engine = KV2Engine(
                client=self.client,
                mount_point=self.namespace,
                **kwargs.get('kv2engine', {})
            )

            if ['connection_name', 'connection_url'] in kwargs.get('dbengine', {}).keys():
                self.dbengine = DBEngine(
                    client=self.client,
                    mount_point=self.namespace,
                    **kwargs.get('dbengine', {})
                )
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.error('[VaultClient]: failed to initialize the vault client: %s', invalid_request)
            raise hvac.exceptions.InvalidRequest

    def authentication(self) -> hvac.Client:
        """
        This method is used to authenticate in the vault server.

        Args:
            None

        Returns:
            (hvac.Client) client
        """
        if self.auth['type'] == 'approle':
            client = hvac.Client(url=self.url, namespace=self.namespace)
            try:
                log.info('[VaultClient]: authenticating in the vault server using the AppRole...')
                response = client.auth.approle.login(
                            role_id=self.auth['approle']['id'],
                            secret_id=self.auth['approle']['secret-id'],
                            mount_point=self.namespace
                )['auth']
                log.info('[VaultClient]: vault token with id %s created successful', response['entity_id'])
            except hvac.exceptions.Forbidden as forbidden:
                log.error('[VaultClient]: failed to login using the AppRole: %s\nplease, check permissions in your policy.hcl', forbidden)
                raise hvac.exceptions.Forbidden

        elif self.auth['type'] == 'token':
            client = hvac.Client(url=self.url, token=self.auth['token'], namespace=self.namespace)
            log.info('[VaultClient]: authenticating in the vault server using the token...')
            if not client.is_authenticated():
                log.error('[VaultClient]: failed to login using the token: %s\nplease, check the token', client.is_authenticated())
                raise hvac.exceptions.InvalidRequest
            log.info('[VaultClient]: vault token with id %s created successful', client.lookup_token()['data']['entity_id'])

        elif self.auth['type'] == 'kubernetes':
            log.info('[VaultClient]: authenticating in the vault server using the Kubernetes...')
            client = hvac.Client(url=self.url, namespace=self.namespace)
            try:
                with open(self.auth['kubernetes'], 'r', encoding='UTF-8') as kubernetes_token:
                    jwt = kubernetes_token.read()
                    Kubernetes(self.client.adapter).login(
                        role=self.namespace,
                        jwt=jwt
                    )
                    log.info('[VaultClient]: vault token with id %s created successful', client.lookup_token()['data']['entity_id'])
            except FileNotFoundError as file_not_found:
                log.error('[VaultClient]: failed to login using the Kubernetes: %s\nplease, check the path to the kubernetes service account token', file_not_found)
                raise FileNotFoundError from file_not_found
            except hvac.exceptions.Forbidden as forbidden:
                log.error('[VaultClient]: failed to login using the Kubernetes: %s\nplease, check the role in the Kubernetes', forbidden)
                raise hvac.exceptions.Forbidden

        return client
