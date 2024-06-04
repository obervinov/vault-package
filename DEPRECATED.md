# Deprecated Methods

This document provides information about deprecated methods in the project.

## Deprecated Methods

| Method | Reason for Deprecation | Date of Deprecation | Alternative | Example of Using the New Method |
| ------ | ---------------------- | ------------------- | ----------- | ------------------------------ |
| `VaultClient.read_secret()` | Revising the code structure for easier scaling when adding new functions | Will be removed in version `3.0.0` | `VaultClient.kv2engine.read_secret()` | ```python<br># Old method<br>result = VaultClient.read_secret(path='test1/creds', key='password')<br><br># New method<br>result = VaultClient.kv2engine.read_secret(path='test1/creds', key='password')``` |
| `VaultClient.write_secret()` | Revising the code structure for easier scaling when adding new functions | Will be removed in version `3.0.0` | `VaultClient.kv2engine.write_secret(path='test1/creds', key='password', value='password')` | ```python<br># Old method<br>result = VaultClient.write_secret(path='test1/creds', key='password', value='password')<br><br># New method<br>result = VaultClient.kv2engine.write_secret(path='test1/creds', key='password', value='password')``` |
| `VaultClient.list_secrets()` | Revising the code structure for easier scaling when adding new functions | Will be removed in version `3.0.0` | `VaultClient.kv2engine.list_secrets(path='test1/creds')` | ```python<br># Old method<br>result = VaultClient.list_secrets(path='test1/creds')<br><br># New method<br>result = VaultClient.kv2engine.list_secrets(path='test1/creds')``` |
