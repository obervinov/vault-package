"""This class is responsible for authentication in the Vault. Supported methods: AppRole, Token, Kubernetes"""
import os
from typing import Union
from dateutil.parser import isoparse
import hvac
import hvac.exceptions
from hvac.api.auth_methods import Kubernetes
from logger import log


class VaultAuth:
    """
    This class is responsible for authentication in the Vault.
    Supported methods: AppRole, Token, Kubernetes.
    """
    def __init__(
            self,
            url: str = None,
            namespace: str = None,
            type: str = None
    ) -> None:
        """
        A method for create 

        Args:
            :param url (str): base URL for the Vault instance.
            :param namespace (str): namespace for the Vault instance.
            :param type (str): type of authentication method. Supported methods: AppRole, Token, Kubernetes.

        Environment Variables:
            VAULT_ADDR: URL of the vault server.
            VAULT_TOKEN: Root token with full access rights.
            VAULT_APPROLE_ID: Approle ID for authentication in the vault server.
            VAULT_APPROLE_SECRETID: Approle Secret ID for authentication in the vault server.
            VAULT_MOUNT_POINT: Mount point for the Approle and Secrets Engine.

        Returns:
            None

        """
        self.auth_type = type
        self.token_expire_date = None

        if url:
            self.url = url
        else:
            self.url = self._get_env('url')
        if namespace:
            self.name = namespace
        else:
            self.namespace = self._get_env('mount_point')

    def _get_env(
        self,
        name: str = None
    ) -> Union[str, dict, None]:
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
                return {'id': os.environ['VAULT_APPROLE_ID'], 'secret-id': os.environ['VAULT_APPROLE_SECRETID']}
            if name == 'mount_point':
                return os.environ['VAULT_MOUNT_POINT']
            return None
        except KeyError as keyerror:
            log.error('[class.%s] failed to extract environment variable for parameter "%s"', __class__.__name__, name)
            raise KeyError(
                "Failed to extract the value of the environment variable. "
                "You need to set an environment variable or pass an argument "
                "when creating an instance of VaultClient(arg=value)"
            ) from keyerror
    
    def _authentication(self) -> hvac.Client:
        """
        This method is used to authenticate in the vault server using the specified method.

        Args:
            None

        Returns:
            (hvac.Client) client
        """
        try:
            if self.auth_type == 'token':
                log.info("[class.%s] logging in vault with Token...", __class__.__name__)
                client = hvac.Client(url=self.url, token=self._get_env('token'))
                log.info("[class.%s] vault Token with id %s created successful", __class__.__name__, client.lookup_token()['data']['id'])

            elif self.auth_type == 'approle':
                client = hvac.Client(url=self.url, namespace=self.name)
                log.info('[class.%s] logging in vault with AppRole...', __class__.__name__)
                response = client.auth.approle.login(
                            role_id=self.approle['id'],
                            secret_id=self.approle['secret-id'],
                            mount_point=self.namespace
                )['auth']
                self.token_expire_date = isoparse(client.lookup_token()['data']['expire_time']).replace(tzinfo=None)
                log.info('[class.%s] vault Token with id %s created successful', __class__.__name__, response['entity_id'])

            elif self.auth_type == 'kubernetes':
                log.info('[class.%s] logging in vault with Kubernetes...', __class__.__name__)
                with open('/var/run/secrets/kubernetes.io/serviceaccount/token', mode='r', encoding='UTF-8') as toke_file:
                    jwt = toke_file.read()
                    Kubernetes(client.adapter).login(role=role, jwt=jwt)

            return client

        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] failed to login using the %s: %s\nplease, check permissions in your policy.hcl',
                __class__.__name__, forbidden, self.auth_type
            )
            raise hvac.exceptions.Forbidden
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.error('[class.%s] failed to login using the AppRole: %s', __class__.__name__, invalid_request)
            raise hvac.exceptions.InvalidRequest
    



    def _prepare_client_secrets(self) -> hvac.Client:
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
            self.approle = self._get_env('approle')
        client = hvac.Client(
            url=self.url,
            namespace=self.name
        )
        try:
            log.info('[class.%s] logging in vault with approle...', __class__.__name__)
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
            self.token_expire_date = isoparse(client.lookup_token()['data']['expire_time']).replace(tzinfo=None)
            log.info('[class.%s] vault token with id %s created successful', __class__.__name__, response['entity_id'])
            return client
        except hvac.exceptions.Forbidden as forbidden:
            log.error('[class.%s] failed to login using the AppRole: %s\nplease, check permissions in your policy.hcl', __class__.__name__, forbidden)
            raise hvac.exceptions.Forbidden
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.error('[class.%s] failed to login using the AppRole: %s', __class__.__name__, invalid_request)
            raise hvac.exceptions.InvalidRequest