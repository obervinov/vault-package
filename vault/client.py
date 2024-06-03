"""
This module contains an implementation over the hvac module for interacting with the Vault Engines.
"""
import os
import json
from typing import Union
from datetime import datetime, timezone
from dateutil.parser import isoparse
import keyring

import hvac
import hvac.exceptions
from hvac.api.auth_methods import Kubernetes

from logger import log
from .kv2_engine import KV2Engine
from .db_engine import DBEngine


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
            >>> 
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
            self.client = self._authentication()
            self.kv2engine = KV2Engine(
                client=self.client,
                mount_point=self.namespace,
                **kwargs.get('kv2engine', {})
            )
            
            
            ### Not ready yet ###
            dbengine_config = kwargs.get('dbengine', {})
            if ['connection_name', 'connection_url'] in dbengine_config:
                self.dbengine = DBEngine(
                    client=self.client,
                    mount_point=self.namespace,
                    **kwargs.get('dbengine', {})
                )
            ### Not ready yet ###
            
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.error('[VaultClient]: failed to initialize the vault client: %s', invalid_request)
            raise hvac.exceptions.InvalidRequest
            
    def _authentication(self) -> hvac.Client:
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
                raise FileNotFoundError
            except hvac.exceptions.Forbidden as forbidden:
                log.error('[VaultClient]: failed to login using the Kubernetes: %s\nplease, check the role in the Kubernetes', forbidden)
                raise hvac.exceptions.Forbidden

        return client
            




    def _prepare_client_configurator(self) -> hvac.Client:
        """
        This method is used to prepare the client for setting up a new vault server
        to work with my typical projects.
        - init
        - unseal
        - upload a policy
        - create a approle
        - create a namespace

        Args:
            None

        Returns:
            (hvac.Client) configurator_client
        """
        client = hvac.Client(
            url=self.url
        )
        if not client.sys.is_initialized():
            self.token = self._init_instance(client=client)['root_token']
        elif self.kwargs.get('token'):
            self.token = self.kwargs.get('token')
        else:
            self.token = self._get_env('token')
        return hvac.Client(
            url=self.url,
            token=self.token
        )

    def _prepare_client_secrets(self) -> hvac.Client:
            client.secrets.kv.v2.configure(
                max_versions=10,
                mount_point=self.name,
                cas_required=False
            )
            self.token_expire_date = isoparse(client.lookup_token()['data']['expire_time']).replace(tzinfo=None)
            log.info('[class.%s] vault token with id %s created successful', __class__.__name__, response['entity_id'])
            return client
        except hvac.exceptions.Forbidden as forbidden:
            log.error('[class.%s] failed to login using the AppRole: %s\nplease, check permissions in your policy.hcl', __class__.__name__, forbidden)
            raise hvac.exceptions.Forbidden
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.error('[class.%s] failed to login using the AppRole: %s', __class__.__name__, invalid_request)
            raise hvac.exceptions.InvalidRequest

    def _init_instance(
        self,
        client: hvac.Client = None
    ) -> dict:
        """
        A method for initialization the vault-server instance.

        Args:
            :param client (hvac.Client): client for initialization vault connections

        Returns:
            (dict) init_data
        """
        log.warning('[class.%s] this vault instance is not initialized: initialization is in progress...', __class__.__name__)
        response = client.sys.initialize()
        try:
            keyring.set_password(self.url, "vault-package:init-data", json.dumps(response))
            log.info(
                '[class.%s] the vault instance was successfully initialized: '
                'sensitive data for managing this instance has been stored in your system keystore',
                __class__.__name__
            )
        except keyring.errors.NoKeyringError:
            temporary_file_path = "/tmp/vault-package-init-data.json"
            log.warning(
                '[class.%s] the vault instance was successfully initialized, '
                'but sensitive information could not be written to the system keystore. '
                'They will be written to a temporary file %s. '
                'Please, move this file to a safe place.',
                __class__.__name__, temporary_file_path
            )
            with open(temporary_file_path, 'w', encoding='UTF-8') as sensitive_file:
                sensitive_file.write(json.dumps(response))

        if client.sys.is_sealed():
            client.sys.submit_unseal_keys(
                keys=[
                    response['keys'][0],
                    response['keys'][1],
                    response['keys'][2]
                ]
            )
            log.info('[class.%s] vault instance has been to unsealed successful', __class__.__name__)
        return response

    def create_namespace(
        self,
        name: str = None
    ) -> str:
        """
        A method for creating a new namespace in the kv v2 engine.

        Args:
            :param name (str): the name of the target namespace.

        Returns:
            (str) namespace_name
        """
        try:
            log.info('[class.%s] creating new namespace "%s" with type "kv2"...', __class__.__name__, name)
            response = self.client.sys.enable_secrets_engine(
                backend_type='kv',
                path=name,
                description=("Namespace is created automatically via the configurator module: https://github.com/obervinov/vault-package"),
                options={'version': 2}
            )
            log.info('[class.%s] namespace "%s" is ready: %s', __class__.__name__, name, response)
            return name
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.warning('[class.%s] namespace already exist: %s', __class__.__name__, invalid_request)
            return name
        except hvac.exceptions.Forbidden as forbidden:
            log.error('[class.%s] failed to create a new namespace: %s\nplease check if your root_token is valid.', __class__.__name__, forbidden)
            raise hvac.exceptions.Forbidden

    def create_policy(
        self,
        name: str = None,
        path: str = None
    ) -> Union[str, None]:
        """
        Method of creating a new policy for approle in the vault.

        Args:
            :param name (str): name of the policy.
            :param path (str): the path to the file with the contents of the policy.

        Returns:
            (str) policy_name
                or
            None
        """
        if os.path.exists(path):
            with open(path, 'rb') as policyfile:
                response = self.client.sys.create_or_update_policy(
                    name=name,
                    policy=policyfile.read().decode("utf-8"),
                )
            policyfile.close()
            log.info('[class.%s] policy "%s" has been created: %s', __class__.__name__, name, response)
            return name
        log.error('[class.%s] the file with the vault policy wasn`t found: %s.', __class__.__name__, path)
        return None

    def create_approle(
        self,
        name: str = None,
        path: str = None,
        policy: str = None,
        token_ttl: str = '1h'
    ) -> Union[dict, None]:
        """
        Method of creating a new approle for authorization in the vault.

        Args:
            :param name (str): name of the AppRole.
            :param path (str): custom mount point for the new AppRole.
            :param policy (str): default policy name for issued tokens.
            :param token_ttl (str): token lifetime during authorization via approle

        Returns:
            (dict) approle_data
                or
            None
        """
        try:
            self.client.sys.enable_auth_method(
                method_type='approle',
                path=path
            )
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.warning('[class.%s] auth method already exist: %s', __class__.__name__, invalid_request)
        response = self.client.auth.approle.create_or_update_approle(
            role_name=name,
            token_policies=[policy],
            token_type='service',
            secret_id_num_uses=0,
            token_num_uses=0,
            token_ttl=token_ttl,
            bind_secret_id=True,
            token_no_default_policy=True,
            mount_point=path
        )
        log.info('[class.%s] approle "%s" has been created %s', __class__.__name__, name, response)
        approle_adapter = hvac.api.auth_methods.AppRole(self.client.adapter)
        approle = {
            'mount-point': name,
            'id': approle_adapter.read_role_id(
                                role_name=name,
                                mount_point=path
                          )["data"]["role_id"],
            'secret-id': approle_adapter.generate_secret_id(
                                role_name=name,
                                mount_point=path
                         )["data"]["secret_id"]
        }
        try:
            keyring.set_password(self.url, "vault-package:approle-data", json.dumps(approle))
            log.info(
                '[class.%s] confidential vault login data via approle has been stored in your system keystore', __class__.__name__)
        except keyring.errors.NoKeyringError:
            temporary_file_path = "/tmp/vault-package-approle-data.json"
            log.warning(
                '[class.%s] confidential vault login data via approle was not saved '
                'to the system keystore. They will be written to a temporary file %s. '
                'Please, move this file to a safe place.',
                __class__.__name__, temporary_file_path
            )
            with open(temporary_file_path, 'w', encoding='UTF-8') as sensitive_file:
                sensitive_file.write(json.dumps(approle))
        log.info('[class.%s] testing login with new approle...', __class__.__name__)
        response = self.client.auth.approle.login(
                        role_id=approle['id'],
                        secret_id=approle['secret-id'],
                        mount_point=path
        )['auth']
        if response['entity_id']:
            log.info('[class.%s] the test login with the new approle was successfully', __class__.__name__,)
            self.client.auth.token.revoke(response['entity_id'])
            log.info('[class.%s] the token %s has been revoked.', __class__.__name__, response['entity_id'])
            return approle
        log.error('[class.%s] failed to get a token with the new approle: %s', __class__.__name__, response)
        return None

