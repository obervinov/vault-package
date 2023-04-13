# Vault Package
[![Release](https://github.com/obervinov/vault-package/actions/workflows/release.yml/badge.svg)](https://github.com/obervinov/vault-package/actions/workflows/release.yml)
[![CodeQL](https://github.com/obervinov/vault-package/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/obervinov/vault-package/actions/workflows/github-code-scanning/codeql)
[![Tests and checks](https://github.com/obervinov/vault-package/actions/workflows/tests.yml/badge.svg?branch=main&event=pull_request)](https://github.com/obervinov/vault-package/actions/workflows/tests.yml)

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/obervinov/vault-package?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/obervinov/vault-package?style=for-the-badge)
![GitHub Release Date](https://img.shields.io/github/release-date/obervinov/vault-package?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/obervinov/vault-package?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/obervinov/vault-package?style=for-the-badge)

## <img src="https://github.com/obervinov/_templates/blob/main/icons/book.png" width="25" title="about"> About this project
This is an additional implementation compared to the **hvac** module.

The main purpose of which is to simplify the use and interaction with vault for my standard projects.

This module contains a set of methods for interacting and quickly installing Vault.

## <img src="https://github.com/obervinov/_templates/blob/main/icons/github-actions.png" width="25" title="github-actions"> GitHub Actions
| Name  | Version |
| ------------------------ | ----------- |
| GitHub Actions Templates | [v1.0.3](https://github.com/obervinov/_templates/tree/v1.0.3) |


## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Support only kv version 2
- Client: Authentication using the application role
- Client: Read the secrets
- Client: List of secrets
- Client: Lay out the secrets
- Client: Secrets of corrections
- Setup: Create a new namespace and engine
- Setup: Create a new application role and a secret ID
- Setup: upload a new policy

## <img src="https://github.com/obervinov/_templates/blob/main/icons/stack2.png" width="20" title="install"> Installing
```bash
# Install current version
pip3 install git+https://github.com/obervinov/vault-package.git#egg=vault
# Install version by branch
pip3 install git+https://github.com/obervinov/vault-package.git@main#egg=vault
# Install version by tag
pip3 install git+https://github.com/obervinov/vault-package.git@v1.0.0#egg=vault
```

## <img src="https://github.com/obervinov/_templates/blob/main/icons/config.png" width="25" title="usage"> Usage example
For kv client
```python
# import modules
import os
import vault as vault

# environment variables
bot_name = os.environ.get(
    'BOT_NAME',
    'mybot'
)
vault_addr = os.environ.get(
    'VAULT_ADDR',
    'http://vault-server:8200'
)
vault_approle_id = os.environ.get(
    'VAULT_APPROLE_ID',
    None
)
vault_approle_secret_id = os.environ.get(
    'VAULT_APPROLE_SECRET_ID',
    None
)

# init vault client
vault_client = VaultClient(
    addr=vault_addr,
    approle_id=vault_approle_id,
    secret_id=vault_approle_secret_id,
    mount_point=bot_name
)
secret_key_value = vc.vault_read_secrets("bucket1/secret1", 'key1')
"""Read target key in secret
type: str
response format: value2
"""

secret_full = vc.vault_read_secrets("bucket1/secret1")
"""Read all keys and values in secret
type: dict
response format: {"key1": "value1", "key2": "value2"}
"""

vc.vault_put_secrets("bucket1/secret1", "my_key", "my_value")
"""Put secret (patch if secret already exist)
"""

vc.vault_list_secrets("bucket1/secret1")
"""List secrets
type: list
response format: ["key1", "key2", "key3"]
"""
```
