"""
This test is necessary to check how the module works with the secrets of the vault instance.
"""
import time
import pytest


@pytest.mark.order(0)
def test_client_secret(approle_client):
    """
    Testing the client of the vault
    """
    assert approle_client is not None
    assert approle_client.client is not None


@pytest.mark.order(1)
def test_write_secret(approle_client, test_data, secret_path):
    """
    Testing writing a secret to the vault
    """
    for key, value in test_data.items():
        response = approle_client.kv2engine.write_secret(
            path=secret_path,
            key=key,
            value=value
        )
        assert response['request_id']


@pytest.mark.order(2)
def test_read_secret(approle_client, test_data, secret_path):
    """
    Testing reading a secret to the vault
    """
    for key, value in test_data.items():
        response = approle_client.kv2engine.read_secret(
          path=secret_path,
          key=key
        )
        assert response == value
        assert isinstance(response, (dict, str))


@pytest.mark.order(3)
def test_list_secrets(approle_client, secret_path):
    """
    Testing checks the reading of the list of secrets from the vault
    """
    response = approle_client.kv2engine.list_secrets(
        path=f"{secret_path.split('/')[0]}/"
    )
    assert f"{secret_path.split('/')[1]}" in response
    assert isinstance(response, list)


@pytest.mark.order(4)
def test_token_ttl_exparation(approle_client, secret_path):
    """
    Testing how does the module work with a token that has expired
    """
    time.sleep(30)
    response = approle_client.kv2engine.list_secrets(
        path=f"{secret_path.split('/')[0]}/"
    )
    assert f"{secret_path.split('/')[1]}" in response
    assert isinstance(response, list)


@pytest.mark.order(5)
def test_read_secret_invalid_path(approle_client, secret_path):
    """
    Testing reading a secret to the vault if the path is invalid (does not exist)
    """
    response_value = approle_client.kv2engine.read_secret(
        path=f"{secret_path}/invalid_path",
        key="invalid_key"
    )
    response_dict = approle_client.kv2engine.read_secret(
        path=f"{secret_path}/invalid_path",
    )
    assert response_value is None
    assert response_dict is None


@pytest.mark.order(6)
def test_list_secrets_invalid_path(approle_client, secret_path):
    """
    Testing checks the reading of the list of secrets from the vault if the path is invalid (does not exist)
    """
    response = approle_client.kv2engine.list_secrets(path=f"{secret_path}/invalid_path")
    assert response == []
    assert isinstance(response, list)


@pytest.mark.order(7)
def test_delete_secret(approle_client, test_data, secret_path):
    """
    Testing deleting a secret from the vault
    """
    for key, value in test_data.items():
        _ = approle_client.kv2engine.write_secret(
            path=secret_path,
            key=key,
            value=value
        )
        response = approle_client.kv2engine.delete_secret(path=secret_path)
        assert response is True
        assert isinstance(response, bool)
