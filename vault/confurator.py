    def _prepare_client_secrets(self) -> hvac.Client:
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

    def _init_instance(
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
        log.warning('[class.%s] this vault instance is not initialized: initialization is in progress...', __class__.__name__)
        response = client.sys.initialize()
        try:
            keyring.set_password(self.url, "vault-package:init-data", json.dumps(response))
            log.info(
                '[class.%s] the vault instance was successfully initialized: '
                'sensitive data for managing this instance has been stored in your system keystore',
                __class__.__name__
            )
        except keyring.errors.NoKeyringError:
            temporary_file_path = "/tmp/vault-package-init-data.json"
            log.warning(
                '[class.%s] the vault instance was successfully initialized, '
                'but sensitive information could not be written to the system keystore. '
                'They will be written to a temporary file %s. '
                'Please, move this file to a safe place.',
                __class__.__name__, temporary_file_path
            )
            with open(temporary_file_path, 'w', encoding='UTF-8') as sensitive_file:
                sensitive_file.write(json.dumps(response))

        if client.sys.is_sealed():
            client.sys.submit_unseal_keys(
                keys=[
                    response['keys'][0],
                    response['keys'][1],
                    response['keys'][2]
                ]
            )
            log.info('[class.%s] vault instance has been to unsealed successful', __class__.__name__)
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
            log.info('[class.%s] creating new namespace "%s" with type "kv2"...', __class__.__name__, name)
            response = self.client.sys.enable_secrets_engine(
                backend_type='kv',
                path=name,
                description=("Namespace is created automatically via the configurator module: https://github.com/obervinov/vault-package"),
                options={'version': 2}
            )
            log.info('[class.%s] namespace "%s" is ready: %s', __class__.__name__, name, response)
            return name
        except hvac.exceptions.InvalidRequest as invalid_request:
            log.warning('[class.%s] namespace already exist: %s', __class__.__name__, invalid_request)
            return name
        except hvac.exceptions.Forbidden as forbidden:
            log.error('[class.%s] failed to create a new namespace: %s\nplease check if your root_token is valid.', __class__.__name__, forbidden)
            raise hvac.exceptions.Forbidden

    def create_policy(
        self,
        name: str = None,
        path: str = None
    ) -> Union[str, None]:
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
            log.info('[class.%s] policy "%s" has been created: %s', __class__.__name__, name, response)
            return name
        log.error('[class.%s] the file with the vault policy wasn`t found: %s.', __class__.__name__, path)
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
            log.warning('[class.%s] auth method already exist: %s', __class__.__name__, invalid_request)
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
        log.info('[class.%s] approle "%s" has been created %s', __class__.__name__, name, response)
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
                '[class.%s] confidential vault login data via approle has been stored in your system keystore', __class__.__name__)
        except keyring.errors.NoKeyringError:
            temporary_file_path = "/tmp/vault-package-approle-data.json"
            log.warning(
                '[class.%s] confidential vault login data via approle was not saved '
                'to the system keystore. They will be written to a temporary file %s. '
                'Please, move this file to a safe place.',
                __class__.__name__, temporary_file_path
            )
            with open(temporary_file_path, 'w', encoding='UTF-8') as sensitive_file:
                sensitive_file.write(json.dumps(approle))
        log.info('[class.%s] testing login with new approle...', __class__.__name__)
        response = self.client.auth.approle.login(
                        role_id=approle['id'],
                        secret_id=approle['secret-id'],
                        mount_point=path
        )['auth']
        if response['entity_id']:
            log.info('[class.%s] the test login with the new approle was successfully', __class__.__name__,)
            self.client.auth.token.revoke(response['entity_id'])
            log.info('[class.%s] the token %s has been revoked.', __class__.__name__, response['entity_id'])
            return approle
        log.error('[class.%s] failed to get a token with the new approle: %s', __class__.__name__, response)
        return None

