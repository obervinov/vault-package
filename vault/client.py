"""
This module contains an implementation over the hvac module for interacting with the Vault api.
"""
import os
import hvac
from logger import log


class VaultClient:
    """
    This class is an implementation over the hvac module.
    This class provides for its operation in two modes:
      - Configure: setting up a new Vault instance to work with my typical projects
        (creating namesapce/approle/policy, init Vault instance)
      - Usage: interactions with secrets in an already configured Vault instance using AppRole
        (read/write/list secrets)
    """
    def __init__(
            self,
            address: str = None,
            namespace: str = None,
            configure: dict = {
                'enabled': False, 
                'token': None,
                'name': None,
                'policy': None
            } | None,
            usage: dict = {
                'enabled': True,
                'approle-id': None,
                'secret-id': None
            } | None
    ) -> None:
        """
        A method for create a new Vault Client instance.
        It works in two modes:
        - Configure: setting up a new Vault instance to work with my typical projects
            (creating namesapce/approle/policy, init Vault instance)
        - Usage: interactions with secrets in an already configured Vault instance using AppRole
            (read/write/list secrets)

        :param address: Base URL for the Vault instance being addressed.
        :type address: str
        :default address: None
        :param namespace: Instance namespace for your kv engine.
            more: https://developer.hashicorp.com/vault/tutorials/enterprise/namespace-structure
        :type namespace: str
        :default namespace: None
        :param configure: Dictionary with parameters for configuring the Vault instance.
        :type configure: dict 
        :default configure: {'enabled': False, 'token': None, 'policy': None} | None
            :param enabled: Initialize the class in the installation mode of the Vault instance.
            :type enabled: bool
            :default enabled: False
            :param token: Root token with with full access rights to configure the Vault instance.
            :type token: str
            :default token: None
            :param name: Name of the new configuration.
            :type name: str
            :default name: None
            :param policy: The path to the file with the contents of the policy.
            :type policy: str
            :default policy: None
        :param usage: Dictionary with parameters for working with Vault instance secrets via AppRole.
        :type usage: dict 
        :default usage: {'enabled': False, 'approle-id': None, 'secret-id': None} | None
            :param enabled: Initialize the class in the mode of working with the secrets of the Vault instance.
            :type enabled: bool
            :default enabled: False
            :param approle-id: AppRole id to receive a token and authorize requests to Vault.
                more: https://www.vaultproject.io/api-docs/auth/approle
            :type approle-id: str
            :default approle-id: None
            :param secret-id: Secret to receive a token and authorize requests to Vault.
                more: https://www.vaultproject.io/api-docs/auth/approle
            :type secret-id: str
            :default secret-id: None
        """
        if address:
            self.address = address
        else:
            self.address = os.environ.get('VAULT_ADDR')

        self.vault_client = hvac.Client(
            url=self.address,
        )

        if not self.vault_client.sys.read_init_status()['initialized']:
            init_data = self.instance_init()
            self.token = init_data['root_token']
            self.keys = init_data['unseal_keys']

        if configure['enabled']:
            if configure['token']:
                self.token = configure['token']
            else:
                self.token = os.environ.get('VAULT_TOKEN')
            self.vault_client = hvac.Client(
                url=self.address,
                token=self.token
            )
            self.namespace = self.create_namespace(
                name=namespace
            )
            self.policy = self.create_policy(
                name=configure['name'],
                path=configure['policy'],
            )
            self.approle = self.create_approle(
                name=configure['name'],
                path=self.namespace,
                policy=self.policy
            )
            with open(
                f"{os.path.expanduser('~')}/.vault_init",
                'w',
                encoding='UTF-8'
            ) as init_file:
                init_file.write(init_data)
            init_file.close()

        if usage['enabled']:
            if not usage['approle-id'] and not usage['secret-id']:
                self.approle['id'] = os.environ.get('VAULT_APPROLE_ID')
                self.approle['secret-id'] = os.environ.get('VAULT_APPROLE_SECRETID')
            else:
                self.approle['id'] = usage['approle-id']
                self.approle['secret-id'] = usage['secret-id']
            self.vault_client = hvac.Client(
                url=self.address,
                namespace=namespace['name'],
            )
            log.info(
                '[class.%s] logging in Vault with approle...',
                __class__.__name__,
            )
            try:
                vault_approle_auth = self.vault_client.auth.approle.login(
                    role_id=self.approle['id'],
                    secret_id=self.approle['secret-id']
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
                    self.approle['id'],
                    forbidden
                )
            except hvac.exceptions.InvalidRequest as invalidrequest:
                log.error(
                    '[class.%s] logging with approle %s invalid request: %s',
                    __class__.__name__,
                    self.approle['id'],
                    invalidrequest
                )


    def instance_init(
        self
    ) -> dict:
        """
        A method for initing the Vault instance.
        """
        log.warning(
            '[class.%s] this vault instance is not initialized. '
            'Initialization is in progress...',
            __class__.__name__
        )
        init_result = self.vault_client.sys.initialize()
        log.info(
            '[class.%s] Initialization completed: %s',
            __class__.__name__,
            init_result
        )
        self.token = init_result['root_token']
        self.vault_client.sys.submit_unseal_key(key=init_result['keys'][0])
        log.info(
            '[class.%s] Instance has been to unsealed',
            __class__.__name__,
        )
        return {
            'root_token': init_result['root_token'],
            'unseal_keys': init_result['keys']
        }


    def create_namespace(
        self,
        name: str = None
    ) -> str:
        """
        A method for creating a new namespace in the Vault kv engine.
        https://developer.hashicorp.com/vault/tutorials/enterprise/namespace-structure

        :param name: The name of the target namespace.
        :type name: str
        :default name: None
        """
        log.info(
            '[class.%s] Creating new namesapce %s with type kv2 in Vault...',
            __class__.__name__,
            name
        )
        namespace = self.vault_client.sys.enable_secrets_engine(
            backend_type='kv',
            path=name,
            description=(
                "Namespace is created automatically via the configrator module"
                "(https://github.com/obervinov/vault-package)"
            ),
            version=2
        )
        log.info(
            '[class.%s] The new namespace %s with type kv2 is ready',
            __class__.__name__,
            name
        )
        self.vault_client = hvac.Client(
                url=self.addr,
                namespace=namespace,
                token=self.token
        )
        log.info(
            '[class.%s] self.vault_client updated to namespace=%s',
            __class__.__name__,
            namespace
        )
        return name


    def create_policy(
        self,
        name: str = None,
        path: str = None
    ) -> str:
        """
        Method of creating a new policy for approle in the Vault.

        :param name: Name of the new policy to create.
        :type name: str
        :default name: None
        :param path: The path to the file with the contents of the policy.
        :type path: str
        :default path: None
        """
        with open(path, 'rb') as policy:
            self.vault_client.sys.create_or_update_policy(
                name=name,
                policy=policy.read(),
            )
        policy.close()
        log.info(
            '[class.%s] The new policy %s has been recorded',
            __class__.__name__,
            name
        )
        return name


    def create_approle(
        self,
        name: str = None,
        path: str = None,
        policy: str = None
    ) -> dict:
        """
        Method of creating a new approle for authorization in the Vault.

        :param name: Name of the new approle to create.
        :type name: str
        :default name: None
        :param path: Custom mount point for the new app role.
        :type path: str
        :default path: None
        :param policy: Default policy name for issued tokens.
        :type policy: str
        :default policy: None
        """
        self.vault_client.sys.enable_auth_method(
            method_type='approle',
            path=path
        )
        response = self.vault_client.auth.approle.create_or_update_approle(
            role_name=name,
            token_policies=[policy],
            token_type='service',
            secret_id_num_uses=0,
            token_num_uses=0,
            token_ttl='15m',
            bind_secret_id=True,
            token_no_default_policy=True,
            mount_point=path
        )
        log.info(
            '[class.%s] The new approle %s has been created: %s',
            __class__.__name__,
            name,
            response
        )
        approle_id = self.vault_client.api.auth_methods.AppRole.read_role_id(
            role_name=name
        )["data"]["role_id"]
        secret_id = self.vault_client.auth.approle.generate_secret_id(
            role_name=name
        )["data"]["secret_id"]
        return {
            'approle-id': approle_id,
            'secret-id': secret_id
        }


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
            if key:
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
