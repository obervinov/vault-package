"""
This module stores fixtures for performing tests.
"""
import pytest
from vault.vault import VaultClient


@pytest.fixture(name="name")
def fixture_name():
    """Returns the project name."""
    return "testapp-1"


@pytest.fixture(name="policy_path")
def fixture_policy_path():
    """Returns the policy path."""
    return "tests/vault/policy.hcl"


@pytest.fixture(name="test_data")
def fixture_test_data():
    """Returns test data for the module."""
    return {
        'username': 'user1',
        'password': 'qwerty',
        'url': 'https://very-important-site.example.com'
    }


@pytest.fixture(name="test_path")
def fixture_test_path():
    """Returns test secret path."""
    return "configuration/mysecret"


@pytest.fixture(name="configurator_client")
def fixture_configurator_client(name, policy_path):
    """Returns client of the configurator"""
    return VaultClient(
                url='http://0.0.0.0:8200',
                name=name,
                new=True
    )


@pytest.fixture(name="secrets_client")
def fixture_secrets_client(approle, name):
    """Returns the client of the secrets."""
    return VaultClient(
            url='http://0.0.0.0:8200',
            name=name,
            approle=approle
    )


@pytest.fixture(name="namespace")
def fixture_namespace(configurator_client, name):
    """Returns the namespace."""
    return configurator_client.create_namespace(
        name=name
    )


@pytest.fixture(name="policy")
def fixture_policy(configurator_client, policy_path, name):
    """Returns the policy path."""
    return configurator_client.create_policy(
        name=name,
        path=policy_path
    )


@pytest.fixture(name="approle")
def fixture_approle(configurator_client, name, policy):
    """Returns the approle data."""
    return configurator_client.create_approle(
        name=name,
        path=name,
        policy=policy
    )
