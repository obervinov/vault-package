"""
This module contains an implementation over the hvac module for interacting with the Vault api.
"""
import os
import hvac
from logger import log


class VaultClient:
    """
    This class is an implementation over the hvac module.
    To simplify and speed up the connection of my projects to vault.
    """

    def __init__(
            self,
            address: str = None,
            name: str = None,
            **kwargs
    ) -> None:
        """
        A method for create a new Vault Client instance.

        Args:
            address (str): base URL for the Vault instance being addressed.
            name (str): the name of the project for which the instance is being created,
                        used for isolation, such as namespace, policy, and approle in Vault.
            **kwargs: dictionary with additional variable parameters

        Keyword Args:
                token (str): root token with full access rights to configure the Vault instance.
                policy (str): the path to the file with the contents of the policy.
                new (bool): if the initial setup of a new instance of the vault server is required.
                approle (dict): dictionary with AppRole credentials.
                                more: https://www.vaultproject.io/api-docs/auth/approle
                    id (str): AppRole id to receive a token and authorize requests to Vault.
                    secret-id (str): secret to receive a token and authorize requests to Vault.

        Returns:
            None

        Examples:
            >>> instance_init = VaultClient(
                    address='http://vault-server:8200',
                    name='myapp-1'
                )
            >>> vault_client = VaultClient(
                    address='http://vault-server:8200',
                    name='myapp-1',
                    approle={'id': '123qwe', 'secret-id': 'qwe123'}
                )
        """
        if address:
            self.address = address
        else:
            self.address = os.environ.get('VAULT_ADDR')
        self.name = name
        self.vault_client = hvac.Client(
            url=self.address,
        )
        self.kwargs = kwargs
        if kwargs.get('new'):
            self.token = None
            self.prepare_instance()
        else:
            self.vault_client = self.prepare_client()

    def prepare_client(
        self
    ) -> hvac.Client:
        """
        This method is used to prepare the client to work with the secrets of the kv v2 engine.

        Args:
            None

        Returns:
            vault_client (hvac.Client)
        """
        approle = {}
        if not self.kwargs.get('approle'):
            approle['id'] = os.environ.get('VAULT_APPROLE_ID')
            approle['secret-id'] = os.environ.get('VAULT_APPROLE_SECRETID')
        else:
            approle = self.kwargs.get('approle')
        vault_client = hvac.Client(
            url=self.address,
            namespace=self.name,
        )
        log.info(
            '[class.%s] logging in Vault with approle...',
            __class__.__name__,
        )
        try:
            vault_approle_auth = vault_client.auth.approle.login(
                role_id=approle['id'],
                secret_id=approle['secret-id']
            )['auth']
            log.info(
                '[class.%s] Vault Token %s created successful',
                __class__.__name__,
                vault_approle_auth['entity_id']
            )
            return vault_client
        except hvac.exceptions.Forbidden as forbidden:
            log.error(
                '[class.%s] logging in with the AppRole '
                'from the VAULT_APPROLE_ID environment variable is forbidden: %s',
                __class__.__name__,
                forbidden
            )
        except hvac.exceptions.InvalidRequest as invalidrequest:
            log.error(
                '[class.%s] logging in with the AppRole '
                'from the VAULT_APPROLE_ID environment variable is invalid request: %s',
                __class__.__name__,
                invalidrequest
            )
        return None

    def prepare_instance(
        self
    ) -> None:
        """
        This method is used to prepare and configure a new Vault-Server
        to work with my typical projects.
        - Init
        - Unseal
        - Uplaod a Policy
        - Create a AppRole

        Args:
            None

        Returns:
            None
        """
        if not self.vault_client.sys.read_init_status()['initialized']:
            token = self.instance_init()['root_token']
        elif self.kwargs.get('token'):
            token = self.kwargs.get('token')
        else:
            token = os.environ.get('VAULT_TOKEN')
        self.vault_client = hvac.Client(
            url=self.address,
            token=token
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

    def instance_init(
        self
    ) -> dict:
        """
        A method for initing the Vault-Server instance.

        Args:
            None

        Returns:
            {'root_token': 'token', 'unseal_keys': 'keys'} (dict)
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
        init_data = {
            'root_token': init_result['root_token'],
            'unseal_keys': init_result['keys']
        }
        with open(f"{os.path.expanduser('~')}/.vault_init", 'w', encoding='UTF-8') as init_file:
            init_file.write(init_data)
        init_file.close()
        return init_data

    def create_namespace(
        self,
        name: str = None
    ) -> str:
        """
        A method for creating a new namespace in the Vault kv engine.
        https://developer.hashicorp.com/vault/tutorials/enterprise/namespace-structure

        Args:
            name (str): the name of the target namespace.

        Returns:
            'policy_name' (str)
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
                url=self.address,
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

        Args:
            name (str): name of the new policy to create.
            path (str): the path to the file with the contents of the policy.

        Retruns:
            'policy_name' (str)
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

        Args:
            name (str): name of the new approle to create.
            path (str): custom mount point for the new app role.
            policy (str): default policy name for issued tokens.

        Returns:
            {'approle-id': approle_id, 'secret-id': secret_id} (dict)
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
        approle = {
            'id': self.vault_client.api.auth_methods.AppRole.read_role_id(
                                role_name=name
                          )["data"]["role_id"],
            'secret-id': self.vault_client.auth.approle.generate_secret_id(
                                role_name=name
                         )["data"]["secret_id"]
        }
        try:
            log.info(
                '[class.%s] Test login with new AppRole data...',
                __class__.__name__
            )
            token = self.vault_client.auth.approle.login(
                            role_id=approle['id'],
                            secret_id=approle['secret-id']
            )['auth']
            if token['entity_id']:
                log.info(
                        '[class.%s] The test login with the new AppRole was successfully: %s\n'
                        'Revocation of the test token...',
                        __class__.__name__,
                        token['entity_id']
                )
                self.vault_client.auth.token.revoke(
                    token['entity_id']
                )
                log.info(
                        '[class.%s] The token has been revoked',
                        __class__.__name__
                )
                log.warning(
                    '[class.%s] New AppRole: %s\nPlease keep this information in a safe place.',
                    __class__.__name__,
                    approle
                )
                return approle
            log.error(
                    '[class.%s] Failed to get a token through the new approle: %s',
                    __class__.__name__,
                    token['entity_id']
            )
            return None
        except hvac.exceptions.VaultError as vaulterror:
            log.error(
                    '[class.%s] Authorization by the new AppRole failed with an error: %s',
                    __class__.__name__,
                    vaulterror
            )
            return None

    def read_secret(
            self,
            path: str = None,
            key: str = None
    ) -> dict:
        """
        A method for read secrets from Vault.

        Args:
            path (str): the path to the secret in vault.
            key (str): the key from which you want to read the value.

        Returns:
            'value' (str)
                or
            {'key': 'value'} (dict)
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

        Args:
            path (str): the path to the secret in vault.
            key (str): the key to write to the secret.
            value (str): the value of the key to write to the secret.

        Returns:
            None
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

        Args:
            path (str): the path to the secret in vault.
            key_value (str): dictionary with keys and their values.

        Returns:
            None
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

        Args:
            path (str): the path to the secret in vault.

        Returns:
            ['key1','key2','key3'] (list)
        """
        return self.vault_client.secrets.kv.v2.list_secrets(
            path=path
        )['data']['keys']
