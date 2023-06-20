"""
This test is necessary to check how the module works with the secrets of the vault instance.
"""
import pytest
import time

@pytest.mark.order(4)
def test_client_secret(secrets_client):
    """
    Testing the client of the vault
    """
    assert secrets_client is not None
    assert secrets_client.client is not None


@pytest.mark.order(5)
def test_write_secret(secrets_client, test_data, secret_path):
    """
    Testing writing a secret to the vault
    """
    for key, value in test_data.items():
        response = secrets_client.write_secret(
            path=secret_path,
            key=key,
            value=value
        )
        assert response['request_id']


@pytest.mark.order(6)
def test_read_secret(secrets_client, test_data, secret_path):
    """
    Testing reading a secret to the vault
    """
    for key, value in test_data.items():
        response = secrets_client.read_secret(
          path=secret_path,
          key=key
        )
        assert response == value
        assert isinstance(response, (dict, str))


@pytest.mark.order(7)
def test_list_secrets(secrets_client, secret_path):
    """
    Testing checks the reading of the list of secrets from the vault
    """
    response = secrets_client.list_secrets(
        path=f"{secret_path.split('/')[0]}/"
    )
    assert f"{secret_path.split('/')[1]}" in response
    assert isinstance(response, list)

@pytest.mark.order(8)
def test_token_ttl_exparation(secrets_client, secret_path):
    """
    Testing how does the module work with a token that has expired
    """
    time.sleep(30)
    response = secrets_client.list_secrets(
        path=f"{secret_path.split('/')[0]}/"
    )
    assert f"{secret_path.split('/')[1]}" in response
    assert isinstance(response, list)
