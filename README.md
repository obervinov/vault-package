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
This is an additional implementation compared to the **hvac** module.</br>
The main purpose of which is to simplify the use and interaction with vault for my standard projects.</br>
This module contains a set of methods for working with `secrets` and `database` engines in **Vault**.


## <img src="https://github.com/obervinov/_templates/blob/main/icons/config.png" width="25" title="envs"> Supported environment variables
| Variable                    | Description                                                                                                  | Example                       |
| --------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------- |
| `VAULT_ADDR`                | Vault server address                                                                                         | `http://vault:8200`                             |
| `VAULT_AUTH_TYPE`           | Type of authentication in the vault server (_token_, _approle_, _kubernetes_)                                | `approle`                               |
| `VAULT_NAMESPACE`           | Namespace with mounted secrets in the vault server                                                           | `project1`                              |
| `VAULT_TOKEN`               | Token for authentication in the vault server                                                                 | `s.123456789qwerty`                        |
| `VAULT_APPROLE_ID`          | [Approle ID](https://developer.hashicorp.com/vault/docs/auth/approle) for get token in the vault server      | `db02de05-fa39-4855-059b-67221c5c2f63`  |
| `VAULT_APPROLE_SECRET_ID`   | [Secret ID](https://developer.hashicorp.com/vault/docs/auth/approle) for get token in the vault server       | `6a174c20-f6de-a53c-74d2-6018fcceff64`  |
| `VAULT_KUBERNETES_SA_TOKEN` | File path to the service account token in the kubernetes cluster                                             | `/var/run/secrets/kubernetes.io/serviceaccount/token`     |

## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="functions"> Supported functions

[__Deprecation Notice__](DEPRECATED.md)

__Authentications__
- `Token`
- `Approle`
- `Kubernetes`

__KV2 Engine__
- `read_secret()`
- `write_secret()`
- `list_secrets()`
- `delete_secret()`

__Database Engine__
- `generate_credentials()`


## <img src="https://github.com/obervinov/_templates/blob/main/icons/requirements.png" width="25" title="mods"> Usage examples
1. Authentication in Vault
   - `token`
   - `approle`
   - `kubernetes`
```python
from vault import VaultClient

# Approle authentication
client = VaultClient(
        url='http://vault:8200',
        namespace='project1',
        auth={
                'type': 'approle',
                'role_id': 'db02de05-fa39-4855-059b-67221c5c2f63',
                'secret_id': '6a1740c20-f6de-a53c-74d2-6018fcceff64'
        }
)

# Token authentication
client = VaultClient(
        url='http://vault:8200',
        namespace='project1',
        auth={
                'type': 'token',
                'token': 's.123456789qwerty'
        }
)

# Kubernetes authentication
client = VaultClient(
        url='http://vault:8200',
        namespace='project1',
        auth={
                'type': 'kubernetes',
                'token': '/var/run/secrets/kubernetes.io/serviceaccount/token'
        }
)
```


2. Interaction with KV2 Secrets Engine
   - `read` specific key from the secret or the full secret body
   - `create` new secret with the specified key and value
   - `update` specific key in the secret with a new value
   - `list` secrets on the specified path
   - `delete` all versions of the secret on the specified path
```python
from vault import VaultClient

client = VaultClient(
        url='http://0.0.0.0:8200',
        namespace='project1',
        auth={
                'type': 'approle',
                'role_id': 'db02de05-fa39-4855-059b-67221c5c2f63',
                'secret_id': '6a174c20-f6de-a53c-74d2-6018fcceff64'
        }
)

# Get value of the specific key in the secret
# type: str
value = client.kv2engine.read_secret(
    path='namespace/secret',
    key='key'
)

# Get the full secret body
# type: dict
secret = client.kv2engine.read_secret(path='namespace/secret')

# Create a new secret with the specified key and value
# type: object
response = client.kv2engine.write_secret(
        path='namespace/secret',
        key='key',
        value='value'
)

# Update specific key in the secret with a new value
# type: object
response = client.kv2engine.write_secret(
        path='namespace/secret',
        key='key',
        value='new_value'
)

# List secrets on the specified path
# type: list
secret_list = client.kv2engine.list_secrets(path='namespace/secret')

# Delete all versions of the secret on the specified path
# type: bool
deleted = client.kv2engine.delete_secret(path='namespace/secret')
```
2. Interaction with Database Engine
   - `generate` new credentials for the specified role
```python
import psycopg2
from vault import VaultClient

client = VaultClient(
        url='http://vault:8200',
        namespace='project1',
        auth={
                'type': 'approle',
                'role_id': 'db02de05-fa39-4855-059b-67221c5c2f63',
                'secret_id': '6a1740c20-f6de-a53c-74d2-6018fcceff64'
        }
)
# Read the secret with the specified path
# type: dict
db_config = client.kv2engine.read_secret(path='project1/db')

# Generate new credentials for the specified role
# type: dict
db_credentials = client.dbengine.generate_credentials(role='project1-role')

# Connect to the database
conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_credentials['username'],
        password=db_credentials['password'],
        host=db_config['host'],
        port=db_config['port']
)
```

## <img src="https://github.com/obervinov/_templates/blob/main/icons/vault.png" width="25" title="usage"> Vault Policy structure
An example with the required permissions and their description for this module is shown in the file [policy.hcl](tests/vault/policy.hcl)

## <img src="https://github.com/obervinov/_templates/blob/main/icons/stack2.png" width="20" title="install"> Installing
```bash
tee -a pyproject.toml <<EOF
[tool.poetry]
name = myproject"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.10"
vault = { git = "https://github.com/obervinov/vault-package.git", tag = "v3.0.1" }

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

poetry install
```

## <img src="https://github.com/obervinov/_templates/blob/main/icons/github-actions.png" width="25" title="github-actions"> GitHub Actions
| Name  | Version |
| ------------------------ | ----------- |
| GitHub Actions Templates | [v2.0.0](https://github.com/obervinov/_templates/tree/v2.0.0) |