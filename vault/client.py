"""
This module contains an implementation over the hvac module for interacting with the Vault api.
"""
import hvac
from logger import log


class VaultClient:
    """
    This class is an implementation over the hvac module.
    Contains methods for reading/writing/enumerating secrets with additional logging and exceptions.
    """

    def __init__(
            self,
            addr: str = "http://localhost:8200",
            namespace: str = None,
            approle: dict = {
                'id': None,
                'secret-id': None
            } | None
    ) -> None:
        """
        A method for create a new Vault Client instance.
        
        :param addr: Base URL for the Vault instance being addressed.
        :type addr: str
        :default addr: http://localhost:8200
        :param namespace: Instance namespace for your kv engine.
                More: https://developer.hashicorp.com/vault/tutorials/enterprise/namespace-structure
        :type namespace: str
        :default namespace: None
        :param approle: Dictionary containing the approle configuration for this instance.
        :type approle: dict
        :default approle: {'id': None, 'secret-id': None} | None
            :param approle.id: Approle id to receive a token and authorize requests to Vault.
                More: https://www.vaultproject.io/api-docs/auth/approle
            :type approle.id: str
            :default approle.id: None
            :param approle.secret-id: Secret to receive a token and authorize requests to Vault.
                More: https://www.vaultproject.io/api-docs/auth/approle
            :type approle.secret-id: str
            :default approle.secret-id: None
        """
        self.addr = addr
        self.vault_client = hvac.Client(
            url=self.addr,
            namespace=namespace['name'],
        )
        log.info(
            '[class.%s] logging in Vault with approle...',
            __class__.__name__,
        )
        try:
            vault_approle_auth = self.vault_client.auth.approle.login(
                role_id=approle['id'],
                secret_id=approle['secret-id']
            )['auth']
            log.info(
                '[class.%s] Vault Token %s created successful',
                __class__.__name__,
                vault_approle_auth['entity_id']
            )
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] logging with approle %s forbidden: %s',
                __class__.__name__,
                approle['id'],
                forbidden
            )
        except hvac.exceptions.InvalidRequest as invalidrequest:
            log.error(
                '[class.%s] logging with approle %s invalid request: %s',
                __class__.__name__,
                approle['id'],
                invalidrequest
            )


    def read_secret(
            self,
            path: str = None,
            key: str = None
    ) -> dict:
        """
        A method for read secrets from Vault.
        
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        :param key: The key from which you want to read the value.
        :type key: str
        :default key: None
        """
        try:
            read_response = self.vault_client.secrets.kv.v2.read_secret_version(
                                    path=path
            )
            if key :
                return read_response['data']['data'][key]
            if not key:
                return read_response['data']['data']
        except hvac.exceptions.InvalidPath as invalidpath:
            log.error(
                '[class.%s] reading secret %s faild: %s',
                __class__.__name__,
                path,
                invalidpath
            )
        return None


    def put_secret(
            self,
            path: str = None,
            key: str = None,
            value: str = None
    ) -> None:
        """
        A method for put secrets from Vault.
        
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        :param key: The key to write to the secret.
        :type key: str
        :default key: None
        :param value: The value of the key to write to the secret.
        :type value: str
        :default value: None
        """
        key_value = {}
        key_value[key] = value
        try:
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=path,
                cas=0,
                secret=key_value
            )
        except hvac.exceptions.InvalidRequest:
            self.patch_secret(path, key_value)


    def patch_secret(
            self,
            path: str = None,
            key_value: str = None
    ) -> None:
        """
        A method for patch secrets from Vault.
        
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        :param key_value: Dictionary with keys and their values.
        :type key_value: str
        :default key_value: None
        """
        self.vault_client.secrets.kv.v2.patch(
            path=path,
            secret=key_value
        )


    def list_secrets(
            self,
            path: str = None
    ) -> list:
        """
        A method for list secrets from Vault.
        
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        """
        return self.vault_client.secrets.kv.v2.list_secrets(
            path=path
        )['data']['keys']
