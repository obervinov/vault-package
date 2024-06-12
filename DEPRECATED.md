# Deprecated Methods

This document provides information about deprecated methods in the project.

## Deprecated Methods

| Method | Reason for Deprecation | Date of Deprecation | Alternative | Example of Using the New Method |
| ------ | ---------------------- | ------------------- | ----------- | ------------------------------ |
| `VaultClient.read_secret()` | Revising the code structure for easier scaling when adding new functions | Was removed in version `3.0.0` | `VaultClient.kv2engine.read_secret()` | ```python<br># Old method<br>result = VaultClient.read_secret(path='test1/creds', key='password')<br><br># New method<br>result = VaultClient.kv2engine.read_secret(path='test1/creds', key='password')``` |
| `VaultClient.write_secret()` | Revising the code structure for easier scaling when adding new functions | Was removed in version `3.0.0` | `VaultClient.kv2engine.write_secret(path='test1/creds', key='password', value='password')` | ```python<br># Old method<br>result = VaultClient.write_secret(path='test1/creds', key='password', value='password')<br><br># New method<br>result = VaultClient.kv2engine.write_secret(path='test1/creds', key='password', value='password')``` |
| `VaultClient.list_secrets()` | Revising the code structure for easier scaling when adding new functions | Was removed in version `3.0.0` | `VaultClient.kv2engine.list_secrets(path='test1/creds')` | ```python<br># Old method<br>result = VaultClient.list_secrets(path='test1/creds')<br><br># New method<br>result = VaultClient.kv2engine.list_secrets(path='test1/creds')``` |
| `VaultClient.get_env()` | Moved to `__init__` of the `VaultClient()` class and now works automatically to retrieve the necessary environment variables to run the module | Was removed in version `3.0.0` | `VaultClient()` | ```python<br># Old method<br>client = VaultClient()<br><br># New method<br>client = VaultClient()``` |
| `VaultClient.prepare_client_configurator()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - | - |
| `VaultClient.prepare_client_secrets()` | Moved to `__init__` of a separate subclass of KV2Engine() and now works automatically to retrieve the necessary environment variables to run the module | Was removed in version `3.0.0` | `KV2Engine()` | ```python<br># Old method<br>client = VaultClient()<br><br># New method<br>client = KV2Engine()``` |
| `VaultClient.init_instance()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - | - |
| `VaultClient.create_namespace()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - | - |
| `VaultClient.create_policy()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - | - |
| `VaultClient.create_approle()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - | - |

## Deprecated Environment Variables

| Variable            | Reason for Deprecation | Date of Deprecation | Alternative | Example of Using the New Variable |
| ------------------- | --------------------------------------------------------------------  | ------------------------------- | ---------------------- | ------------------------------ |
| `VAULT_MOUNT_POINT` | The name of the variable has been changed to a more appropriate name  | Was replaced in version `3.0.0` | `VAULT_NAMESPACE` | ```bash<br># Old variable<br>export VAULT_MOUNT_POINT='test1'<br><br># New variable<br>export VAULT_NAMESPACE='test1'``` |
| `VAULT_APPROLE_SECRETID` | A cosmetic change to keep the eye from twitching.                | Was replaced in version `3.0.0` | `VAULT_APPROLE_SECRET_ID` | ```bash<br># Old variable<br>export VAULT_APPROLE_SECRETID='test1'<br><br># New variable<br>export VAULT_APPROLE_SECRET_ID='test1'``` |
