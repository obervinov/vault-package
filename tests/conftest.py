"""
This module stores fixtures for performing tests.
"""
import os
import pytest
from vault.vault import VaultClient


@pytest.fixture(name="url", scope='session')
def fixture_url():
    """Returns the vault url"""
    if os.getenv("CI"):
        return "http://localhost:8200"
    return "http://0.0.0.0:8200"


@pytest.fixture(name="name", scope='session')
def fixture_name():
    """Returns the project name"""
    return "testapp-1"


@pytest.fixture(name="policy_path", scope='session')
def fixture_policy_path():
    """Returns the policy path"""
    return "tests/vault/policy.hcl"


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


@pytest.fixture(name="configurator_client", scope='session')
def fixture_configurator_client(url, name):
    """Returns client of the configurator"""
    return VaultClient(
                url=url,
                name=name,
                new=True
    )


@pytest.fixture(name="secrets_client", scope='session')
def fixture_secrets_client(url, approle, name):
    """Returns the client of the secrets"""
    return VaultClient(
            url=url,
            name=name,
            approle=approle
    )


@pytest.fixture(name="namespace", scope='session')
def fixture_namespace(configurator_client, name):
    """Returns the namespace"""
    return configurator_client.create_namespace(
        name=name
    )


@pytest.fixture(name="policy", scope='session')
def fixture_policy(configurator_client, policy_path, name):
    """Returns the policy path."""
    return configurator_client.create_policy(
        name=name,
        path=policy_path
    )


@pytest.fixture(name="approle", scope='session')
def fixture_approle(configurator_client, name, policy):
    """Returns the approle data"""
    return configurator_client.create_approle(
        name=name,
        path=name,
        policy=policy,
        token_ttl='15s'
    )
