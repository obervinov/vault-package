"""
This module contains an implementation over the hvac module for interacting with the Vault api.
"""
import os
import json
import hvac
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
            :param url (str): base URL for the Vault instance being urled.
            :param name (str): the name of the project for which an instance is being created,
                               this name will be used for isolation mechanisms such as:
                               namespace, policy, approle
            :param **kwargs (dict): dictionary with additional variable parameters

        Keyword Args:
            :param new (bool): to activate the "initial setup" mode of vault-server.
            :param token (str): root token with full access to configure the vault-server.
            :param policy (str): the path to the file with the contents of the policy.
            :param approle (dict): dictionary with approle credentials.
                :param id (str): approle-id to receive a token.
                :param secret-id (str): secret-id to receive a token.

        Returns:
            None

        Examples:
            >>> init_instance = VaultClient(
                    url='http://vault-server:8200',
                    name='myapp-1',
                    policy='vault/policy.hcl',
                )
            >>> instance_prepare = VaultClient(
                    url='http://vault-server:8200',
                    name='myapp-1',
                    policy='vault/policy.hcl',
                    token=hvs.123qwe
                )
            >>> vault_client = VaultClient(
                    url='http://vault-server:8200',
                    name='myapp-1',
                    approle={'id': '123qwe', 'secret-id': 'qwe123'}
                )
        """
        if url:
            self.url = url
        else:
            self.url = os.environ.get('VAULT_ADDR')
        self.name = name
        self.kwargs = kwargs
        self.vault_client = hvac.Client(
            url=self.url
        )
        if kwargs.get('new'):
            self.token = None
            self.prepare_instance()
        else:
            self.approle = None
            self.vault_client = self.prepare_client_kv2()

    def prepare_instance(
        self
    ) -> None:
        """
        This method is used to prepare and configure a new vault-server
        to work with my typical projects.
        - Init
        - Unseal
        - Uplaod a policy
        - Create a approle
        - Create a namespace

        Args:
            None

        Returns:
            None
        """
        if not self.vault_client.sys.is_initialized():
            self.token = self.init_instance()
        elif self.kwargs.get('token'):
            self.token = self.kwargs.get('token')
        else:
            self.token = os.environ.get('VAULT_TOKEN')

        self.vault_client = hvac.Client(
            url=self.url,
            token=self.token
        )
        namespace = self.create_namespace(
            name=self.name
        )
        policy = self.create_policy(
            name=self.name,
            path=self.kwargs.get('policy'),
        )
        self.create_approle(
            name=self.name,
            path=namespace,
            policy=policy
        )

    def prepare_client_kv2(
        self
    ) -> hvac.Client:
        """
        This method is used to prepare the client to work with the secrets of the kv v2 engine.

        Args:
            None

        Returns:
            (hvac.Client) vault_client_kv2
                or
            None
        """
        if self.kwargs.get('approle'):
            self.approle = self.kwargs.get('approle')
        else:
            self.approle['id'] = os.environ.get('VAULT_APPROLE_ID')
            self.approle['secret-id'] = os.environ.get('VAULT_APPROLE_SECRETID')

        vault_client = hvac.Client(
            url=self.url,
            namespace=self.name,
        )

        try:
            log.info(
                '[class.%s] logging in vault with approle...',
                __class__.__name__,
            )
            response = vault_client.auth.approle.login(
                role_id=self.approle['id'],
                secret_id=self.approle['secret-id']
            )['auth']
            log.info(
                '[class.%s] vault token with id %s created successful',
                __class__.__name__,
                response['entity_id']
            )
            return vault_client
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] logging in with the approle '
                'from the VAULT_APPROLE_ID environment variable is forbidden: %s',
                __class__.__name__,
                forbidden
            )
        except hvac.exceptions.InvalidRequest as invalidrequest:
            log.error(
                '[class.%s] logging in with the approle '
                'from the VAULT_APPROLE_ID environment variable is invalid request: %s',
                __class__.__name__,
                invalidrequest
            )
        return None

    def init_instance(
        self
    ) -> str:
        """
        A method for initing the vault-server instance.

        Args:
            None

        Returns:
            (str) 'root_token'
                or
            None
        """
        log.warning(
            '[class.%s] this vault instance is not initialized: '
            'initialization is in progress...',
            __class__.__name__
        )
        response = self.vault_client.sys.initialize()
        keys_store = f"{os.path.expanduser('~')}/.vaultinit"
        with open(keys_store, 'w', encoding='UTF-8') as initfile:
            initfile.write(json.dumps(response))
        initfile.close()
        log.warning(
            '[class.%s] the vault instance was successfully initialized: '
            'sensitive information for managing this instance has been stored in %s',
            __class__.__name__,
            keys_store
        )

        if self.vault_client.sys.is_sealed():
            self.vault_client.sys.submit_unseal_keys(
                keys=[response['keys'][0], response['keys'][1], response['keys'][2]]
            )
            log.info(
                '[class.%s] vault instance has been to unsealed successfull',
                __class__.__name__,
            )
        return response['root_token']

    def create_namespace(
        self,
        name: str = None
    ) -> str:
        """
        A method for creating a new namespace in the kv v2 engine.

        Args:
            :param name (str): the name of the target namespace.

        Returns:
            (str) 'namespace'
                or
            None
        """
        try:
            log.info(
                '[class.%s] creating new namesapce "%s" with type "kv2"...',
                __class__.__name__,
                name
            )
            response = self.vault_client.sys.enable_secrets_engine(
                backend_type='kv',
                path=name,
                description=(
                    "Namespace is created automatically via the configrator module"
                    "(https://github.com/obervinov/vault-package)"
                ),
                version=2
            )
            log.info(
                '[class.%s] namespace "%s" is ready: %s',
                __class__.__name__,
                name,
                response
            )
            return name
        except hvac.exceptions.InvalidRequest as invalidrequest:
            log.warning(
                '[class.%s] namespace already exist: %s',
                __class__.__name__,
                invalidrequest
            )
            return name
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] failed to create a new namespace: %s\n'
                'please check if your root_token is valid.',
                __class__.__name__,
                forbidden
            )
            return None

    def create_policy(
        self,
        name: str = None,
        path: str = None
    ) -> str:
        """
        Method of creating a new policy for approle in the vault.

        Args:
            :param name (str): name of the new policy to create.
            :param path (str): the path to the file with the contents of the policy.

        Retruns:
            (str) 'policy'
                or
            None
        """
        if os.path.exists(path):
            with open(path, 'rb') as policyfile:
                response = self.vault_client.sys.create_or_update_policy(
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
            '[class.%s] the file with the vault policy was not found: %s.',
            __class__.__name__,
            path
        )
        return None

    def create_approle(
        self,
        name: str = None,
        path: str = None,
        policy: str = None
    ) -> None:
        """
        Method of creating a new approle for authorization in the vault.

        Args:
            :param name (str): name of the new approle to create.
            :param path (str): custom mount point for the new app role.
            :param policy (str): default policy name for issued tokens.

        Returns:
           None
        """
        try:
            self.vault_client.sys.enable_auth_method(
                method_type='approle',
                path=path
            )
        except hvac.exceptions.InvalidRequest as invalidrequest:
            log.warning(
                '[class.%s] auth method already exist: %s',
                __class__.__name__,
                invalidrequest
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
            '[class.%s] approle "%s" has been created %s',
            __class__.__name__,
            name,
            response
        )
        approle_adapter = hvac.api.auth_methods.AppRole(
            self.vault_client.adapter
        )
        approle = {
            'name': name,
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
            log.info(
                '[class.%s] testing login with new approle...',
                __class__.__name__
            )
            response = self.vault_client.auth.approle.login(
                            role_id=approle['id'],
                            secret_id=approle['secret-id'],
                            mount_point=path
            )['auth']
            if response['entity_id']:
                log.info(
                        '[class.%s] the test login with the new approle was successfully: '
                        'revocation of the test token %s ...',
                        __class__.__name__,
                        response['entity_id']
                )
                self.vault_client.auth.token.revoke(
                    response['entity_id']
                )
                log.info(
                        '[class.%s] the token %s has been revoked.',
                        __class__.__name__,
                        response['entity_id']
                )
                print(
                    f"!!! AppRole Data: {approle}\n"
                    "!!! Please keep this information in a safe place."
                )
            else:
                log.error(
                        '[class.%s] failed to get a token through the new approle: %s',
                        __class__.__name__,
                        response['entity_id']
                )
        except hvac.exceptions.VaultError as vaulterror:
            log.error(
                    '[class.%s] authorization by the new approle failed with an error: %s',
                    __class__.__name__,
                    vaulterror
            )

    def read_secret(
        self,
        path: str = None,
        key: str = None
    ) -> dict:
        """
        A method for read secrets from vault.

        Args:
            :param path (str): the path to the secret in vault.
            :param key (str): specify the key if you want to get only the value of a specific key,
                              and not the entire dictionary

        Returns:
            (str) 'value'
                or
            (dict) {'key': 'value'}
        """
        try:
            response = self.vault_client.secrets.kv.v2.read_secret_version(
                path=path
            )
            if key:
                return response['data']['data'][key]
            if not key:
                return response['data']['data']
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
        A method for put secrets from vault.

        Args:
            :param path (str): the path to the secret in vault.
            :param key (str): the key to write to the secret.
            :param value (str): the value of the key to write to the secret.

        Returns:
            None
        """
        secret = {key: value}
        try:
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=path,
                cas=0,
                secret=secret
            )
        except hvac.exceptions.InvalidRequest:
            self.patch_secret(path, secret)

    def patch_secret(
            self,
            path: str = None,
            secret: str = None
    ) -> None:
        """
        A method for patch secrets from vault.

        Args:
            :param path (str): the path to the secret in vault.
            :param secret (str): dictionary with keys and their values.

        Returns:
            None
        """
        self.vault_client.secrets.kv.v2.patch(
            path=path,
            secret=secret
        )

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
        return self.vault_client.secrets.kv.v2.list_secrets(
            path=path
        )['data']['keys']
