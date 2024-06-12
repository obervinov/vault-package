"""
This test is necessary to check how the module works with the secrets of the vault instance.
"""
import pytest


@pytest.mark.order(8)
def test_generate_credentials(approle_client):
    """
    Testing the generation of database credentials
    """
    response = approle_client.dbengine.generate_credentials(role='test-role')
    assert isinstance(response, dict)
    assert response['username'] is not None
    assert response['password'] is not None
