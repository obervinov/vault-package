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
| GitHub Actions Templates | [v1.0.4](https://github.com/obervinov/_templates/tree/v1.0.4) |

## <img src="https://github.com/obervinov/_templates/blob/main/icons/config.png" width="25" title="envs"> Supported environment variables
| Variable  | Description | Example |
| ------------- | ------------- | ------------- |
| `VAULT_ADDR`  | URL of the vault server | `http://vault.example.com:8200` |
| `VAULT_TOKEN` | Root token with full access rights | `hvs.123qwerty` |
| `VAULT_APPROLE_ID`  | [Approle ID](https://developer.hashicorp.com/vault/docs/auth/approle) for authentication in the vault server | `db02de05-fa39-4855-059b-67221c5c2f63` |
| `VAULT_APPROLE_SECRETID`  | [Approle Secret ID](https://developer.hashicorp.com/vault/docs/auth/approle) for authentication in the vault server |  `6a174c20-f6de-a53c-74d2-6018fcceff64` |

## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Support only kv version 2
- Client: Authentication using the application role
- Client: Read the secrets
- Client: List the secrets
- Client: Update the secrets
- Client: Create the secrets
- Setup: Create a new namespace and enable engine
- Setup: Create a new application role and a secret ID
- Setup: Upload a new policy

## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="mods"> Usage examples
This module can operate in two types of modes:
1. working with `secrets` via the kv version 2 engine (`read`/`write`/`update`/`list` secrets)
```python
from vault import VaultClient

client = VaultClient(
            url='http://0.0.0.0:8200',
            name='project1',
            approle={
                'id': 'db02de05-fa39-4855-059b-67221c5c2f63',
                'secret-id': '6a174c20-f6de-a53c-74d2-6018fcceff64'
            }
)

# Get only the key value from the secret
# type: str
value = client.read_secret(
    "namespace/secret", 'key'
)

# Get full dict with the secret body
# type: dict
secret = client.read_secret(
    "namespace/secret"
)

# Write new data to a secret
# type: requests.response
response = client.write_secret(
     "namespace/secret",
     "key",
     "value"
)

# Get a list of secrets on the specified path
# type: list
response = client.list_secrets(
    "bucket1/secret1"
)
```
2. working with the vault instance `configuration` (create or update `engine`/`namespace`/`policy`/`approle`)</br>
__preparing an existing vault server for your project__
```python
from vault import VaultClient


configurator = VaultClient(
                url='http://0.0.0.0:8200',
                name='project1',
                new=True,
)

# Enable the kv v2 engine and create a new namespace
# type: str
namespace = configurator.create_namespace(
        name='namespace1'
)

# Download a new policy from a local file
# type: str
policy = configurator.create_policy(
        name='policy1',
        path='tests/vault/policy.hcl'
)

# Create a new approle
# type: dict
approle = configurator.create_approle(
        name='approle1',
        path=namespace,
        policy=policy
)
```
__preparing a new (not initialized) vault server for your project__ 
```python
from vault import VaultClient


configurator = VaultClient(
                url='http://0.0.0.0:8200',
                name='project1',
                new=True,
                token='hvs.123456789qwerty'
)

# Enable the kv v2 engine and create a new namespace
# type: str
namespace = configurator.create_namespace(
        name='namespace1'
)

# Download a new policy from a local file
# type: str
policy = configurator.create_policy(
        name='policy1',
        path='tests/vault/policy.hcl'
)

# Create a new approle
# type: dict
approle = configurator.create_approle(
        name='approle1',
        path=namespace,
        policy=policy
)
```

## <img src="https://github.com/obervinov/_templates/blob/main/icons/vault.png" width="25" title="usage"> Vault Policy structure
An example with the required permissions and their description in [policy.hcl](tests/vault/policy.hcl)

## <img src="https://github.com/obervinov/_templates/blob/main/icons/stack2.png" width="20" title="install"> Installing
```bash
# Install current version
pip3 install git+https://github.com/obervinov/vault-package.git#egg=vault
# Install version by branch
pip3 install git+https://github.com/obervinov/vault-package.git@main#egg=vault
# Install version by tag
pip3 install git+https://github.com/obervinov/vault-package.git@v1.0.0#egg=vault
```
