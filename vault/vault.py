"""
This module contains an implementation over the hvac module for interacting with the Vault api.
"""
import os
import json
from datetime import datetime, timezone
from dateutil.parser import isoparse
import hvac
import keyring
from logger import log


class VaultClient:
    """
    This class is an implementation over the hvac module.
    To simplify and speed up the connection of my projects to vault.
    """

    def __init__(
            self,
            url: str = None,
            name: str = None,
            **kwargs
    ) -> None:
        """
        A method for create a new Vault Client instance.

        Args:
            :param url (str): base URL for the Vault instance.
            :param name (str): the name of the project for which an instance is being created,
                               this name will be used for isolation mechanisms such as:
                               namespace, policy, approle
            :param **kwargs (dict): dictionary with additional variable parameters

        Keyword Args:
            :param new (bool): starting in the "preparing a vault instance for a new project" mode.
            :param token (str): root token with full access to configure the vault-server.
            :param approle (dict): dictionary with approle credentials.
                :param id (str): approle-id to receive a token.
                :param secret-id (str): secret-id to receive a token.

        Returns:
            None

        Examples:
            >>> init_instance = VaultClient(
                    url='http://vault:8200',
                    name='myapp-1'
                )
            >>> prepare_instance = VaultClient(
                    url='http://vault:8200',
                    name='myapp-1'
                    token=hvs.123qwerty
                )
            >>> client_secrets = VaultClient(
                    url='http://vault:8200',
                    name='myapp-1',
                    approle={'id': '123qwerty', 'secret-id': 'qwerty123'}
                )
        """
        if url:
            self.url = url
        else:
            self.url = self.get_env('url')

        self.name = name
        self.kwargs = kwargs

        if kwargs.get('new'):
            self.token = None
            self.client = self.prepare_client_configurator()
        else:
            self.approle = {}
            self.token_expire_date = None
            self.client = self.prepare_client_secrets()

    def get_env(
        self,
        name: str = None
    ) -> str | dict | None:
        """
        This method is used to extract a value from an environment variable and error handling

        Args:
            :param name (str): name of the environment variable

        Returns:
            (str) value
                or
            (dict) values
                or
            None
        """
        try:
            if name == 'url':
                return os.environ['VAULT_ADDR']
            if name == 'token':
                return os.environ['VAULT_TOKEN']
            if name == 'approle':
                return {
                    'id': os.environ['VAULT_APPROLE_ID'],
                    'secret-id': os.environ['VAULT_APPROLE_SECRETID']
                }
            return None
        except KeyError as keyerror:
            log.error(
                '[class.%s] failed to extract environment variable for parameter "%s"',
                __class__.__name__,
                name
            )
            raise KeyError(
                "Failed to extract the value of the environment variable. "
                "You need to set an environment variable or pass an argument "
                "when creating an instance of VaultClient(arg=value)"
            ) from keyerror

    def prepare_client_configurator(
        self
    ) -> hvac.Client:
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
            self.token = self.init_instance(
                client=client
            )['root_token']
        elif self.kwargs.get('token'):
            self.token = self.kwargs.get('token')
        else:
            self.token = self.get_env('token')
        return hvac.Client(
            url=self.url,
            token=self.token
        )

    def prepare_client_secrets(
        self
    ) -> hvac.Client:
        """
        This method is used to prepare the client to work with the secrets of the kv v2 engine.
        - read secrets
        - write secrets
        - list secrets

        Args:
            None

        Returns:
            (hvac.Client) secrets_client
        """
        if self.kwargs.get('approle'):
            self.approle = self.kwargs.get('approle')
        else:
            self.approle = self.get_env('approle')
        client = hvac.Client(
            url=self.url,
            namespace=self.name
        )
        try:
            log.info(
                '[class.%s] logging in vault with approle...',
                __class__.__name__,
            )
            response = client.auth.approle.login(
                        role_id=self.approle['id'],
                        secret_id=self.approle['secret-id'],
                        mount_point=self.name
            )['auth']
            client.secrets.kv.v2.configure(
                max_versions=10,
                mount_point=self.name,
                cas_required=False
            )
            self.token_expire_date = isoparse(
                client.lookup_token()['data']['expire_time']
            ).replace(tzinfo=None)
            log.info(
                '[class.%s] vault token with id %s created successful',
                __class__.__name__,
                response['entity_id']
            )
            return client
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] failed to log in using the AppRole: %s\n'
                'please, check permissions in your policy.hcl',
                __class__.__name__,
                forbidden
            )
            raise hvac.exceptions.Forbidden
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.error(
                '[class.%s] failed to log in using the AppRole: %s',
                __class__.__name__,
                invalid_request
            )
            raise hvac.exceptions.InvalidRequest

    def init_instance(
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
        log.warning(
            '[class.%s] this vault instance is not initialized: '
            'initialization is in progress...',
            __class__.__name__
        )
        response = client.sys.initialize()
        try:
            keyring.set_password(self.url, "vault-package:init-data", json.dumps(response))
            log.info(
                '[class.%s] the vault instance was successfully initialized: '
                'sensitive data for managing this instance has been stored in your system keystore',
                __class__.__name__
            )
        except keyring.errors.NoKeyringError:
            log.warning(
                '[class.%s] the vault instance was successfully initialized: '
                'but sensitive data for managing this instance was not saved.',
                __class__.__name__
            )

        if client.sys.is_sealed():
            client.sys.submit_unseal_keys(
                keys=[
                    response['keys'][0],
                    response['keys'][1],
                    response['keys'][2]
                ]
            )
            log.info(
                '[class.%s] vault instance has been to unsealed successful',
                __class__.__name__,
            )
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
            log.info(
                '[class.%s] creating new namespace "%s" with type "kv2"...',
                __class__.__name__,
                name
            )
            response = self.client.sys.enable_secrets_engine(
                backend_type='kv',
                path=name,
                description=(
                    "Namespace is created automatically via the configurator module: "
                    "https://github.com/obervinov/vault-package"
                ),
                options={
                    'version': 2
                }
            )
            log.info(
                '[class.%s] namespace "%s" is ready: %s',
                __class__.__name__,
                name,
                response
            )
            return name
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.warning(
                '[class.%s] namespace already exist: %s',
                __class__.__name__,
                invalid_request
            )
            return name
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] failed to create a new namespace: %s\n'
                'please check if your root_token is valid.',
                __class__.__name__,
                forbidden
            )
            raise hvac.exceptions.Forbidden

    def create_policy(
        self,
        name: str = None,
        path: str = None
    ) -> str | None:
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
            log.info(
                '[class.%s] policy "%s" has been created: %s',
                __class__.__name__,
                name,
                response
            )
            return name
        log.error(
            '[class.%s] the file with the vault policy wasn`t found: %s.',
            __class__.__name__,
            path
        )
        return None

    def create_approle(
        self,
        name: str = None,
        path: str = None,
        policy: str = None,
        token_ttl: str = '1h'
    ) -> dict | None:
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
            log.warning(
                '[class.%s] auth method already exist: %s',
                __class__.__name__,
                invalid_request
            )
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
        log.info(
            '[class.%s] approle "%s" has been created %s',
            __class__.__name__,
            name,
            response
        )
        approle_adapter = hvac.api.auth_methods.AppRole(
            self.client.adapter
        )
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
                '[class.%s] confidential vault login data via approle '
                'has been stored in your system keystore',
                __class__.__name__
            )
        except keyring.errors.NoKeyringError:
            log.warning(
                '[class.%s] confidential vault login data via approle was not saved.',
                __class__.__name__
            )

        log.info(
            '[class.%s] testing login with new approle...',
            __class__.__name__
        )
        response = self.client.auth.approle.login(
                        role_id=approle['id'],
                        secret_id=approle['secret-id'],
                        mount_point=path
        )['auth']
        if response['entity_id']:
            log.info(
                '[class.%s] the test login with the new approle was successfully',
                __class__.__name__,
            )
            self.client.auth.token.revoke(
                response['entity_id']
            )
            log.info(
                    '[class.%s] the token %s has been revoked.',
                    __class__.__name__,
                    response['entity_id']
            )
            return approle
        log.error(
                '[class.%s] failed to get a token with the new approle: %s',
                __class__.__name__,
                response
        )
        return None

    def read_secret(
        self,
        path: str = None,
        key: str = None
    ) -> str | dict:
        """
        A method for read secret from vault.

        Args:
            :param path (str): the path to the secret in vault.
            :param key (str): specify the key if you want to get only the value of a specific key.

        Returns:
            (str) 'value'
                or
            (dict) {'key': 'value'}
        """
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.name,
                raise_on_deleted_version=True
            )
            if key:
                return response['data']['data'][key]
            if not key:
                return response['data']['data']
        except hvac.exceptions.InvalidPath as invalid_path:
            log.error(
                '[class.%s] reading secret %s failed: %s',
                __class__.__name__,
                path,
                invalid_path
            )
            raise hvac.exceptions.InvalidPath
        except hvac.exceptions.Forbidden as forbidden:
            if self.token_expire_date <= datetime.now(timezone.utc).replace(tzinfo=None):
                self.client = self.prepare_client_secrets()
                return self.read_secret(
                    path=path,
                    key=key
                )
            log.error(
                '[class.%s] reading secret failed: %s',
                __class__.__name__,
                forbidden
            )
            raise hvac.exceptions.Forbidden
        return None

    def write_secret(
        self,
        path: str = None,
        key: str = None,
        value: str = None
    ) -> object:
        """
        A method for write secret from vault.

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
            # check if a secret exists
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.name,
                raise_on_deleted_version=True
            )['data']['data']
            secret[key] = value
            # update an existing secret
            return self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret,
                mount_point=self.name
            )
        except hvac.exceptions.InvalidPath:
            # if the secret doesn't exist
            return self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={key: value},
                mount_point=self.name
            )
        except hvac.exceptions.Forbidden as forbidden:
            if self.token_expire_date <= datetime.now(timezone.utc).replace(tzinfo=None):
                self.client = self.prepare_client_secrets()
                return self.write_secret(
                    path=path,
                    key=key,
                    value=value
                )
            log.error(
                '[class.%s] writing secret failed: %s',
                __class__.__name__,
                forbidden
            )
            raise hvac.exceptions.Forbidden

    def list_secrets(
        self,
        path: str = None
    ) -> list:
        """
        A method for list secrets from vault.

        Args:
            :param path (str): the path to the secret in vault.

        Returns:
            (list) ['key1','key2','key3']
        """
        try:
            return self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.name
            )['data']['keys']
        except hvac.exceptions.Forbidden as forbidden:
            if self.token_expire_date <= datetime.now(timezone.utc).replace(tzinfo=None):
                self.client = self.prepare_client_secrets()
                return self.list_secrets(
                    path=path
                )
            log.error(
                '[class.%s] listing secret failed: %s',
                __class__.__name__,
                forbidden
            )
            raise hvac.exceptions.Forbidden
