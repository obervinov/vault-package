# Vault Package
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/obervinov/vault-package?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/obervinov/vault-package?style=for-the-badge)
![GitHub Release Date](https://img.shields.io/github/release-date/obervinov/vault-package?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/obervinov/vault-package?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/obervinov/vault-package?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/instaloader?style=for-the-badge)

## <img src="https://github.com/obervinov/content/blob/main/ico/1945958.png" width="25" title="about"> About this project
This is an additional implementation over the **hvac** module.

The main purpose of which is simplified use and interaction with vault for standard projects.

This module contains a collection of methods for working with vault.



## <img src="https://github.com/obervinov/content/blob/main/ico/8823344.png" width="25" title="functions"> Support only kv version 2
- Read secrets
- List secrets
- Put secrets
- Patch secrets

## <img src="https://github.com/obervinov/content/blob/main/ico/8840892.png" width="20" title="install"> Installing
```bash
pip3 install git+https://github.com/obervinov/vault-package.git@main#egg=vault
```

## <img src="https://github.com/obervinov/content/blob/main/ico/7264022.png" width="25" title="usage"> Usage example
```python
# Import module
import os
import vault as vault

# Environment variables #
vault_mount_point = os.environ.get('VAULT_MOUNT_PATH', 'kv')
vault_addr = os.environ.get('VAULT_ADDR', 'http://localhost:8200')
vault_approle_id = os.environ.get('VAULT_APPROLE_ID', 'not set')
vault_approle_secret_id = os.environ.get('VAULT_APPROLE_SECRET_ID', 'not set')

# Init class
vc = vault.VaultClient(
               vault_addr,
               vault_approle_id,
               vault_approle_secret_id,
               vault_mount_point
)

# Read target key in secret
secret_key_value = vc.vault_read_secrets("bucket1/secret1", 'key1')

# Read all keys and values in secret
secret_full = vc.vault_read_secrets("bucket1/secret1")

# Put secret (patch if secret already exist)
vc.vault_put_secrets("bucket1/secret1", "my_key", "my_value")

# List secrets
vc.vault_list_secrets("bucket1/secret1")
```
