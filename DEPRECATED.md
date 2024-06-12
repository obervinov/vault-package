# Deprecated Methods

This document provides information about deprecated methods in the project.

## Deprecated Methods

| Method | Reason for Deprecation | Date of Deprecation | Alternative |
| ------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- |
| `VaultClient.read_secret()` | Revising the code structure for easier scaling when adding new functions | Was removed in version `3.0.0` | `VaultClient.kv2engine.read_secret()` |
| `VaultClient.write_secret()` | Revising the code structure for easier scaling when adding new functions | Was removed in version `3.0.0` | `VaultClient.kv2engine.write_secret()` |
| `VaultClient.list_secrets()` | Revising the code structure for easier scaling when adding new functions | Was removed in version `3.0.0` | `VaultClient.kv2engine.list_secrets()` |
| `VaultClient.get_env()` | Moved to `__init__` of the `VaultClient()` class and now works automatically to retrieve the necessary environment variables to run the module | Was removed in version `3.0.0` | `VaultClient()` |
| `VaultClient.prepare_client_configurator()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - |
| `VaultClient.prepare_client_secrets()` | Moved to `__init__` of a separate subclass of KV2Engine() and now works automatically to retrieve the necessary environment variables to run the module | Was removed in version `3.0.0` | `KV2Engine()` |
| `VaultClient.init_instance()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - |
| `VaultClient.create_namespace()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - |
| `VaultClient.create_policy()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - |
| `VaultClient.create_approle()` | All functionality related to the configuration of a new vault instance has been removed from the module (as the preparation of infrastructures is not part of the concept of this module). | Was removed in version `3.0.0` | - |

## Deprecated Environment Variables

| Variable            | Reason for Deprecation | Date of Deprecation | Alternative |
| ------------------- | --------------------------------------------------------------------  | ------------------------------- | ---------------------- |
| `VAULT_MOUNT_POINT` | The name of the variable has been changed to a more appropriate name  | Was replaced in version `3.0.0` | `VAULT_NAMESPACE` |
| `VAULT_APPROLE_SECRETID` | A cosmetic change to keep the eye from twitching.                | Was replaced in version `3.0.0` | `VAULT_APPROLE_SECRET_ID` |
