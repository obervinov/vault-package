# Vault Package
[![Release](https://github.com/obervinov/vault-package/actions/workflows/release.yaml/badge.svg)](https://github.com/obervinov/vault-package/actions/workflows/release.yaml)
[![CodeQL](https://github.com/obervinov/vault-package/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/obervinov/vault-package/actions/workflows/github-code-scanning/codeql)
[![Tests and checks](https://github.com/obervinov/vault-package/actions/workflows/pr.yaml/badge.svg?branch=main&event=pull_request)](https://github.com/obervinov/vault-package/actions/workflows/pr.yaml)

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/obervinov/vault-package?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/obervinov/vault-package?style=for-the-badge)
![GitHub Release Date](https://img.shields.io/github/release-date/obervinov/vault-package?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/obervinov/vault-package?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/obervinov/vault-package?style=for-the-badge)

## <img src="https://github.com/obervinov/_templates/blob/main/icons/book.png" width="25" title="about"> About this project
This is an additional implementation compared to the **hvac** module.

The main purpose of which is to simplify the use and interaction with vault for my standard projects.

This module contains a set of methods for working with secrets and quickly configuring Vault.

## <img src="https://github.com/obervinov/_templates/blob/main/icons/github-actions.png" width="25" title="github-actions"> GitHub Actions
| Name  | Version |
| ------------------------ | ----------- |
| GitHub Actions Templates | [v1.0.12](https://github.com/obervinov/_templates/tree/v1.0.12) |

## <img src="https://github.com/obervinov/_templates/blob/main/icons/config.png" width="25" title="envs"> Supported environment variables
| Variable  | Description | Example |
| ------------- | ------------- | ------------- |
| `VAULT_ADDR`  | URL of the vault server | `http://vault.example.com:8200` |
| `VAULT_TOKEN` | Root token with full access rights | `hvs.123qwerty` |
| `VAULT_APPROLE_ID`  | [Approle ID](https://developer.hashicorp.com/vault/docs/auth/approle) for authentication in the vault server | `db02de05-fa39-4855-059b-67221c5c2f63` |
| `VAULT_APPROLE_SECRETID`  | [Approle Secret ID](https://developer.hashicorp.com/vault/docs/auth/approle) for authentication in the vault server |  `6a174c20-f6de-a53c-74d2-6018fcceff64` |
| `VAULT_MOUNT_POINT`  |  Mount point for Approle and Secrets Engine. Can be used instead of the `name` argument in the `VaultClient` class |  `myproject-1` |

## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Supported functions
__The client can only work with the KV v2 engine__
- Client: Authentication using the AppRole
- Client: Reading a secrets
- Client: Listing a secrets
- Client: Writing a secrets
- Configurator: Initializing a new vault instance
- Configurator: Unsealing a new vault instance
- Configurator: Creating a new namespace and enabling the kvv2 engine
- Configurator: Creating a new AppRole ID and a generating a new AppRole Secret ID
- Configurator: Uploading a new vault policy

## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="mods"> Usage examples
This module can operate in two types of modes:
1. Working with the kv secrets engine (v2): `read`/`write`/`update`/`list` of secrets
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
    path='namespace/secret',
    key='key'
)

# Get full dict with the secret body
# type: dict
secret = client.read_secret(
    path='namespace/secret'
)

# Write new data to a secret
# type: requests.response
response = client.write_secret(
     path='namespace/secret',
     key='key',
     value='value'
)

# Get a list of secrets on the specified path
# type: list
response = client.list_secrets(
    path='namespace/secret1'
)
```
2. Working with the `configuration` of a vault instance: create or update `engine`/`namespace`/`policy`/`approle`</br>

_preparing a new (not initialized) vault server for your project_
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

_preparing an existing vault server for your project_
```python
from vault import VaultClient

configurator = VaultClient(
                url='http://0.0.0.0:8200',
                name='project1',
                new=False,
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
tee -a pyproject.toml <<EOF
[tool.poetry]
name = myproject"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.10"
vault = { git = "https://github.com/obervinov/vault-package.git", tag = "v2.0.2" }

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

poetry install
```
