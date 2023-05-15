"""
This test is necessary to check how the module works with the configuration of the vault instance.
"""
import pytest


@pytest.mark.order(1)
def test_create_namespace(namespace, name):
    """
    Testing the creation of a new namespace.
    """
    assert namespace == name
    assert isinstance(namespace, str)


@pytest.mark.order(2)
def test_create_policy(policy):
    """
    Testing the creation of a new policy.
    """
    assert policy is not None
    assert isinstance(policy, str)


@pytest.mark.order(3)
def test_create_approle(approle):
    """
    Testing the creation of a new approle.
    """
    assert isinstance(approle, dict)
    assert approle['id'] is not None
    assert approle['secret-id'] is not None
    assert approle['mount-point'] is not None
