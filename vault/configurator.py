"""
This module contains an implementation on top of the hvac module
for configuring the Vault instance via the api.
"""
import hvac
from logger import log


class VaultConfigurator:
    """
    This class is an implementation over the hvac module.
    Contains methods for creating policy/approle/namespace secrets
    with additional logging and exceptions.
    """

    def __init__(
            self,
            addr: str = "http://localhost:8200",
            token: str = None,
            namespace: dict = {
                'create': False,
                'name': None
                } | None,
            approle: dict = {
                'create': False,
                'name': None
            } | None
    ) -> None:
        """
        A method for create a new Vault Configurator instance.
        
        :param addr: Base URL for the Vault instance being addressed.
        :type addr: str
        :default addr: http://localhost:8200
        :param token: Root token with full access rights to the Vault
        :type token: str
        :default token: None
        :param namespace: Instance namespace for your kv engine.
                More: https://developer.hashicorp.com/vault/tutorials/enterprise/namespace-structure
        :type namespace: dict
        :default namespace: {'create': False, 'name': None} | None
            :param namespace.create: If the target namespace does not exist and needs to be created.
            :type namespace.create: str
            :default namespace.create: False
            :param namespace.name: The name of the target namespace.
            :type namespace.name: str
            :default namespace.name: None
        :param approle: Dictionary containing the approle configuration for this instance.
        :type approle: dict
        :default approle: {'create': False, 'name': None} | None
            :param approle.create: Used only if you need to create a new approle
                (root token required).
            :type approle.create: bool
            :default approle.create: False
            :param approle.name: Name of the approle to create.
            :type approle.name: str
            :default approle.name: None
        """
        self.addr = addr
        self.approle = approle
        if namespace['create']:
            self.vault_client = hvac.Client(
                url=self.addr,
                namespace=self.create_namespace(),
                token=token
            )
        else:
            self.vault_client = hvac.Client(
                url=self.addr,
                namespace=namespace['name'],
                token=token
            )
        log.info(
            '[class.%s] logging in Vault with root token...',
            __class__.__name__
        )
        if self.vault_client.is_authenticated():
            log.info(
                '[class.%s] Vault login with root token successful',
                __class__.__name__
            )
        else:
            log.error(
                '[class.%s] Vault login with root token faild',
                __class__.__name__
            )


    def create_namespace(
        self,
        path: str = None
    ) -> str:
        """
        A method for creating a new namespace in the Vault kv engine.
        
        :param path: Root path of the new namespace.
        :type path: str
        :default path: None
        """
        log.info(
            '[class.%s] Creating new namesapce %s with type kv2 in Vault...',
            __class__.__name__,
            path
        )
        self.vault_client.sys.enable_secrets_engine(
            backend_type='kv',
            path=path,
            description=(
                "Namespace is created automatically via the configrator module"
                "(https://github.com/obervinov/vault-package)"
            ),
            version=2
        )
        log.info(
            '[class.%s] The new namespace %s with type kv2 is ready',
            __class__.__name__,
            path
        )
        return path


    def create_policy(
        self,
        name: str = None,
        path: str = None
    ):
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


    def create_approle(
        self,
        name: str = None,
        path: str = None,
        policy: str = None,
        descritpion: str = None
    ) -> str:
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
        :param descritpion: Brief description of the app role and binding to the project.
        :type descritpion: str
        :default descritpion: None
        """
        self.vault_client.sys.enable_auth_method(
            method_type='approle',
            descritpion=descritpion,
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
        return response
