"""This module contains an implementation over the hvac module for interacting with the vault api"""
import hvac
from logger import log


class VaultClient:
    """This class is an implementation over the hvac module.
    Contains methods for reading/placing/listing secrets with additional doping and exceptions.
    """

    def __init__(
            self,
            addr: str = "http://localhost:8200",
            approle_id: str = None,
            secret_id: str = None,
            mount_point: str = "kv"
    ) -> None:
        """A function for create a new vault client instance.
        :param addr: Base URL for the Vault instance being addressed.
        :type addr: str
        :default addr: http://localhost:8200
        :param approle_id: Approle id to receive a token and then authorize requests to Vault.
                More: https://www.vaultproject.io/api-docs/auth/approle
        :type approle_id: str
        :default approle_id: None
        :param approle_secret_id: Secret id to receive a token and then authorize requests to Vault.
                More: https://www.vaultproject.io/api-docs/auth/approle
        :type approle_secret_id: str
        :default approle_secret_id: None
        :param mount_point: Default kv secret mount point.
                More: https://developer.hashicorp.com/vault/tutorials/enterprise/namespace-structure
        :type mount_point: str
        :default mount_point: kv
        """
        self.addr = addr
        self.approle_id = approle_id
        self.secret_id = secret_id
        self.mount_point = mount_point
        self.vault_object = hvac.Client(url=self.addr,)

        log.info(
            f"[class.{__class__.__name__}] "
            f"logging in Vault with approle..."
        )
        try:
            vault_approle_auth = self.vault_object.auth.approle.login(
                role_id=self.approle_id,
                secret_id=self.secret_id
            )['auth']
            log.info(
                f"[class.{__class__.__name__}] "
                f"Vault Token {vault_approle_auth['entity_id']} created successful"
            )
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                f"[class.{__class__.__name__}] "
                f"logging with approle forbidden, "
                f"please check capabilities ['read', 'list', 'create', 'update] "
                f"for '{mount_point}/config'\n"
                f"{forbidden}"
            )
        except hvac.exceptions.InvalidRequest as invalidrequest:
            log.error(
                f"[class.{__class__.__name__}] "
                f"logging with approle invalid request, "
                f"please check your role-id or secret-id\n"
                f"{invalidrequest}"
            )

    def vault_read_secrets(
            self,
            path: str = None,
            key: str = None
    ) -> dict:
        """A function for read secrets from Vault.
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        :param key: The key from which you want to read the value.
        :type key: str
        :default key: None
        """
        try:
            read_response = self.vault_object.secrets.kv.v2.read_secret_version(
                                    path=path,
                                    mount_point=self.mount_point,
            )
            if key :
                return read_response['data']['data'][key]
            if not key:
                return read_response['data']['data']
        except hvac.exceptions.InvalidPath as invalidpath:
            log.error(
                f"[class.{__class__.__name__}] "
                f"reading secret {path} faild\n"
                f"{invalidpath}"
            )
        return None

    def vault_put_secrets(
            self,
            path: str = None,
            key: str = None,
            value: str = None
    ) -> None:
        """A function for put secrets from Vault.
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
            self.vault_object.secrets.kv.v2.create_or_update_secret(
                path=path,
                cas=0,
                secret=key_value,
                mount_point=self.mount_point,
            )
        except hvac.exceptions.InvalidRequest:
            self.vault_patch_secrets(path, key_value)

    def vault_patch_secrets(
            self,
            path: str = None,
            key_value: str = None
    ) -> None:
        """A function for patch secrets from Vault.
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        :param key_value: Dictionary with keys and their values.
        :type key_value: str
        :default key_value: None
        """
        self.vault_object.secrets.kv.v2.patch(
            path=path,
            secret=key_value,
            mount_point=self.mount_point,
        )

    def vault_list_secrets(
            self,
            path: str = None
    ) -> list:
        """A function for list secrets from Vault.
        :param path: The path to the secret in vault.
        :type path: str
        :default path: None
        """
        return self.vault_object.secrets.kv.v2.list_secrets(
            path=path,
            mount_point=self.mount_point
        )['data']['keys']
