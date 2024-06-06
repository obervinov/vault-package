"""
This module stores fixtures for performing tests.
"""
import os
import pytest
import hvac
from vault.client import VaultClient


@pytest.fixture(name="url", scope='session')
def fixture_url():
    """Returns the vault url"""
    if os.getenv("CI"):
        return "http://localhost:8200"
    return "http://0.0.0.0:8200"


@pytest.fixture(name="namespace", scope='session')
def fixture_name():
    """Returns the project name"""
    return "testapp-1"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="prepare_vault", scope='session')
def fixture_prepare_vault(url, namespace, policy_path):
    """Returns the vault client"""
    client = hvac.Client(url=url)
    init_data = client.sys.initialize()
    # Unseal the vault
    if client.sys.is_sealed():
        client.sys.submit_unseal_keys(keys=[init_data['keys'][0], init_data['keys'][1], init_data['keys'][2]])
    # Authenticate in the vault server using the root token
    client = hvac.Client(url=url, token=init_data['root_token'])
    # Create policy
    with open(policy_path, 'rb') as policyfile:
        _ = client.sys.create_or_update_policy(
            name=namespace,
            policy=policyfile.read().decode("utf-8"),
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
    return {
        'id': approle_adapter.read_role_id(role_name=namespace, mount_point=namespace)["data"]["role_id"],
        'secret-id': approle_adapter.generate_secret_id(role_name=namespace, mount_point=namespace)["data"]["secret_id"]
    }


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
def fixture_configurator_client(url, namespace, prepare_vault):
    """Returns client of the configurator"""
    return VaultClient(
        url=url,
        namespace=namespace,
        auth={
            'type': 'approle',
            'approle': {
                'id': prepare_vault['id'],
                'secret-id': prepare_vault['secret-id']
            }
        }
    )
