"""
This module stores fixtures for performing tests.
"""
import os
import pytest
import hvac
from vault.client import VaultClient


@pytest.fixture(name="vault_url", scope='session')
def fixture_vault_url():
    """Returns the vault url"""
    if os.getenv("CI"):
        return "http://localhost:8200"
    return "http://0.0.0.0:8200"


@pytest.fixture(name="postgres_url", scope='session')
def fixture_postgres_url():
    """Returns the postgres url"""
    return "postgresql://{{username}}:{{password}}@0.0.0.0:5432/postgres?sslmode=disable"


@pytest.fixture(name="namespace", scope='session')
def fixture_name():
    """Returns the project name"""
    return "testapp-1"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="prepare_vault", scope='session')
def fixture_prepare_vault(vault_url, namespace, policy_path, postgres_url):
    """Returns the vault client"""
    client = hvac.Client(url=vault_url)
    init_data = client.sys.initialize()

    # Unseal the vault
    if client.sys.is_sealed():
        client.sys.submit_unseal_keys(keys=[init_data['keys'][0], init_data['keys'][1], init_data['keys'][2]])
    # Authenticate in the vault server using the root token
    client = hvac.Client(url=vault_url, token=init_data['root_token'])

    # Create policy
    with open(policy_path, 'rb') as policyfile:
        _ = client.sys.create_or_update_policy(
            name=namespace,
            policy=policyfile.read().decode("utf-8"),
        )

    # Create Namespace
    _ = client.sys.enable_secrets_engine(
        backend_type='kv',
        path=namespace,
        options={'version': 2}
    )

    # Prepare AppRole for the namespace
    client.sys.enable_auth_method(
        method_type='approle',
        path=namespace
    )
    _ = client.auth.approle.create_or_update_approle(
        role_name=namespace,
        token_policies=[namespace],
        token_type='service',
        secret_id_num_uses=0,
        token_num_uses=0,
        token_ttl='15s',
        bind_secret_id=True,
        token_no_default_policy=True,
        mount_point=namespace
    )
    approle_adapter = hvac.api.auth_methods.AppRole(client.adapter)

    # Prepare database engine configuration
    client.sys.enable_secrets_engine(
        backend_type='database',
        path='database'
    )
    _ = client.secrets.database.configure(
        name='postgresql',
        plugin_name='postgresql-database-plugin',
        allowed_roles=[namespace],
        connection_url=postgres_url,
        username='vault',
        password='vault',
        db_name='postgres',
        mount_point='database'
    )

    return {
        'id': approle_adapter.read_role_id(role_name=namespace, mount_point=namespace)["data"]["role_id"],
        'secret-id': approle_adapter.generate_secret_id(role_name=namespace, mount_point=namespace)["data"]["secret_id"]
    }


@pytest.fixture(name="prepare_postgres", scope='session')
def fixture_prepare_postgres(postgres_url):
    """Prepare database engine configuration"""
    # Configure database engine
    _ = hvac.Client().secrets.database.configure(
        name="postgresql",
        plugin_name="postgresql-database-plugin",
        verify_connection=True,
        allowed_roles=["test_role"],
        username="postgres",
        password="postgres",
        connection_url=postgres_url
    )

    # Create role for the database
    _ = hvac.Client().secrets.database.create_role(
        name="test_role",
        db_name="postgres",
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
        default_ttl="1h",
        max_ttl="24h"
    )


@pytest.fixture(name="test_data", scope='session')
def fixture_test_data():
    """Returns test data for the module"""
    return {
        'username': 'user1',
        'password': 'qwerty',
        'url': 'https://very-important-site.example.com'
    }


@pytest.fixture(name="secret_path", scope='session')
def fixture_secret_path():
    """Returns the path to the test secret"""
    return "configuration/mysecret"


@pytest.fixture(name="approle_client", scope='session')
def fixture_configurator_client(vault_url, namespace, prepare_vault):
    """Returns client of the configurator"""
    return VaultClient(
        url=vault_url,
        namespace=namespace,
        auth={
            'type': 'approle',
            'approle': {
                'id': prepare_vault['id'],
                'secret-id': prepare_vault['secret-id']
            }
        }
    )
