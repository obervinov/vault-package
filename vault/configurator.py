"""This module contains the VaultConfigurator class for preparing the vault server for project needs."""
import os
import json
from typing import Union
import keyring

import hvac
import hvac.exceptions

from logger import log


class VaultConfigurator:
    """
    This class is responsible for preparing the vault server for project needs.
    Supported methods for:
        - create namespace
        - create policy
        - create AppRole
    """
    def __init__(
        self,
        url: str = None,
        namespace: str = None,
        token: str = None
    ) -> None:
        """
        A method for creating an instance of the VaultConfigurator.

        Args:
            :param url (str): the url of the vault server.
            :param namespace (str): the namespace of the vault server.
            :param token (str): the token for the vault server.

        Returns:
            None
        """
        try:
            log.info('[VaultConfigurator]: extracting the configuration for the vault configurator...')

            if url:
                self.url = url
            else:
                self.url = os.environ.get('VAULT_ADDR')

            if namespace:
                self.namespace = namespace
            else:
                self.namespace = os.environ.get('VAULT_NAMESPACE')

            if token:
                self.token = token
            else:
                self.token = os.environ.get('VAULT_TOKEN')

            log.info('[VaultConfigurator]: configuration has been successfully extracted for vault %s', self.url)
        except KeyError as keyerror:
            raise KeyError(
                "Failed to extract the value of the environment variable. "
                "You need to set an environment variable or pass an argument when creating an instance of VaultConfigurator(arg=value)"
            ) from keyerror

        self.client = hvac.Client(url=self.url)
        if not self.client.sys.is_initialized():
            self.token = self.init_instance()['root_token']
        self.client = hvac.Client(url=self.url, token=self.token)

    def init_instance(self) -> dict:
        """
        A method for initialization the vault instance.

        Args:
            None

        Returns:
            (dict) {
                'keys': [str, str, str],
                'keys_base64': [str, str, str],
                'root_token': str,
                'root_token_accessor': str
            }
        """
        log.warning('[VaultConfigurator]: the vault instance is not initialized: initialization is in progress...')
        response = self.client.sys.initialize()
        try:
            keyring.set_password(self.url, "vault-package:init-data", json.dumps(response))
            log.info(
                '[VaultConfigurator]: the vault instance was successfully initialized: '
                'sensitive data for managing this instance has been stored in your system keystore'
            )
        except keyring.errors.NoKeyringError:
            temporary_file_path = "/tmp/vault-package-init-data.json"
            log.warning(
                '[VaultConfigurator]: the vault instance was successfully initialized, but sensitive information could not be written to the system keystore. '
                'They will be written to a temporary file %s. Please, move this file to a safe place.',
                temporary_file_path
            )
            with open(temporary_file_path, 'w', encoding='UTF-8') as sensitive_file:
                sensitive_file.write(json.dumps(response))

        if self.client.sys.is_sealed():
            self.client.sys.submit_unseal_keys(keys=[response['keys'][0], response['keys'][1], response['keys'][2]])
            log.info('[VaultConfigurator]: vault instance has been to unsealed successful')

        log.info('[VaultConfigurator]: the vault instance has been initialized')
        return response

    def create_kv2_namespace(self) -> Union[dict, None]:
        """
        A method for creating a new namespace in the kv v2 engine.

        Args:
            None

        Returns:
            (dict) response
                or
            None
        """
        try:
            log.info('[VaultConfigurator]: creating new kv2 namespace "%s" ...', self.namespace)
            response = self.client.sys.enable_secrets_engine(
                backend_type='kv',
                path=self.namespace,
                description=("Namespace is created automatically via the VaultConfigurator class from https://github.com/obervinov/vault-package"),
                options={'version': 2}
            )
            log.info('[VaultConfigurator]: kv2 namespace "%s" has been created: %s', self.namespace, response)
            return response
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.warning('[VaultConfigurator]: kv2 namespace already exist: %s', invalid_request)
            return None
        except hvac.exceptions.Forbidden as forbidden:
            log.error('[VaultConfigurator]: failed to create a new kv2 namespace: %s\nplease check if your root_token is valid.', forbidden)
            raise hvac.exceptions.Forbidden

    def create_policy(
        self,
        policy_file: str = None,
    ) -> Union[str, None]:
        """
        Method of creating a new policy for role (AppRole or Kubernetes) in the vault.

        Args:
            :param policy_file (str): path to the file with the vault policy.

        Returns:
            (str) policy_name
                or
            None
        """
        if os.path.exists(policy_file):
            with open(policy_file, 'rb') as policyfile:
                response = self.client.sys.create_or_update_policy(name=self.namespace, policy=policyfile.read().decode("utf-8"))
            log.info('[VaultConfigurator]: new policy "%s" has been created: %s', self.namespace, response)
            return self.namespace
        log.error('[VaultConfigurator]: the file with the vault policy wasn`t found: %s.', policy_file)
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
            log.warning('[VaultConfigurator]: auth method already exist: %s', __class__.__name__, invalid_request)
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
        log.info('[VaultConfigurator]: approle "%s" has been created %s', __class__.__name__, name, response)
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
                '[VaultConfigurator]: confidential vault login data via approle has been stored in your system keystore', __class__.__name__)
        except keyring.errors.NoKeyringError:
            temporary_file_path = "/tmp/vault-package-approle-data.json"
            log.warning(
                '[VaultConfigurator]: confidential vault login data via approle was not saved '
                'to the system keystore. They will be written to a temporary file %s. '
                'Please, move this file to a safe place.',
                __class__.__name__, temporary_file_path
            )
            with open(temporary_file_path, 'w', encoding='UTF-8') as sensitive_file:
                sensitive_file.write(json.dumps(approle))
        log.info('[VaultConfigurator]: testing login with new approle...', __class__.__name__)
        response = self.client.auth.approle.login(
                        role_id=approle['id'],
                        secret_id=approle['secret-id'],
                        mount_point=path
        )['auth']
        if response['entity_id']:
            log.info('[VaultConfigurator]: the test login with the new approle was successfully', __class__.__name__,)
            self.client.auth.token.revoke(response['entity_id'])
            log.info('[VaultConfigurator]: the token %s has been revoked.', __class__.__name__, response['entity_id'])
            return approle
        log.error('[VaultConfigurator]: failed to get a token with the new approle: %s', __class__.__name__, response)
        return None

