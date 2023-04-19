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
            namespace: str = None
    ) -> None:
        """
        A method for create a new Vault Configurator instance.
        
        :param addr: Base URL for the Vault instance being addressed.
        :type addr: str
        :default addr: http://localhost:8200
        :param token: Root token with full access rights to the Vault
        :type token: str
        :default token: None
        :param namespace: The name of the target namespace.
        :type namespace: str
        :default namespace: None
        """
        self.addr = addr
        self.token = token
        self.vault_client = hvac.Client(
            url=self.addr,
            token=token,
            namespace=namespace
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
        policy: str = None,
        descritpion: str = None
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
            role_name=name,
            metadata=descritpion
        )["data"]["secret_id"]
        return {
            'approle-id': approle_id,
            'secret-id': secret_id
        }
