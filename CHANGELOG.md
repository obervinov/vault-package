# Change Log
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).



## v2.0.0 - 2023-04-08
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.1.1...v2.0.0 by @obervinov in https://github.com/obervinov/vault-package/pull/10
#### 🐛 Bug Fixes
* refactoring all `doc-strings` in class `VaultClient()`
* renamed the directory with modules: `src` -> `vault`
* fixed warnings from `.flake8` and `.pylintrc`
* removed condition `- '!main'` for [.github/workflows/tests.yml](https://github.com/obervinov/vault-package/blob/v2.0.0/.github/workflows/tests.yml#L3-L8) (this is done for the correct display of the badge in [README.md](https://github.com/obervinov/vault-package/blob/v2.0.0/README.md?plain=1#L4) on the `main` brunch)
#### 💥 Breaking Changes
* changed all arguments in `__init__` from the `VaultClient()` class:
   `mount_point: str = "kv"` -> `namespace: str = None`
   `approle_id: str = None`, `secret_id: str = None` -> `approle: dict = {'id': None, 'secret-id': None} | None`
* changed log format `f-string` -> `%s-lazzy`
* updated [SECURITY.md](https://github.com/obervinov/vault-package/blob/v2.0.0/SECURITY.md) policy
* renamed file with `VaultClient` class: `vault.py` -> `client.py`
* renamed methods in `VaultClient` class: `vault_read_secrets()` -> `read_secret()`, `vault_put_secrets()` -> `put_secret()`, `vault_patch_secrets()` -> `patch_secret()` `vault_list_secrets()` -> `list_secrets()`
* moved `mount_point=self.mount_point` from `vault_read_secrets()`, `vault_put_secrets()`, `vault_patch_secrets()`, `vault_list_secrets()` to `self.vault_client = hvacClient(url=self.addr, namespace=namespace['name'])` of `__init__()`
#### 🚀 Features
* added new `VaultConfigurator()` class to automate and speed up the setup of a new vault instance for my projects
* all workflows migrated to version `v1.0.3`
* updated logger version `git = "https://github.com/obervinov/logger-package.git", tag = "v1.0.1"`
* added condition `paths: ['vault/**']` for `.github/workflows/release.yml` action (this is done so that you can update the documentation without creating an `MR` and a `new release`)
#### 📚 Documentation
* updated the template body in `pull_request_template.md`
* updated `description` in `pyproject.toml`



## v1.1.1 - 2023-03-01
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.1.0...v1.1.1 by @obervinov in https://github.com/obervinov/vault-package/pull/9
#### 🐛 Bug Fixes
* fixed `install_requires` in [setup.py](https://github.com/obervinov/vault-package/blob/main/setup.py)
* added parameter dependency_links in [setup.py](https://github.com/obervinov/vault-package/blob/main/setup.py)
#### 📚 Documentation
* rewritten the sample code in [README.md](https://github.com/obervinov/vault-package/blob/main/README.md)



## v1.1.0 - 2023-02-28
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.0.3...v1.1.0 by @obervinov in https://github.com/obervinov/vault-package/pull/5
#### 🐛 Bug Fixes
* updated the code in accordance with the recommendations of **flake8** and **pylint**
* adjusted [pyproject.toml](https://github.com/obervinov/vault-package/blob/main/pyproject.toml) and [setup.py](https://github.com/obervinov/vault-package/blob/main/setup.py) for package delivery
#### 📚 Documentation
* updated and expanded the documentation in the file [README.md](https://github.com/obervinov/vault-package/blob/main/README.md)
#### 💥 Breaking Changes
* global **code recycling**: _updated all exceptions events_, _removed old artifacts_, _fixed redundant logging_ and _more comments added to the code_
#### 🚀 Features
* added github actions: **flake8**, **pylint** and **create release**
* added [SECURITY](https://github.com/obervinov/vault-package/blob/main/SECURITY.md)
* added [ISSUE_TEMPLATE](https://github.com/obervinov/vault-package/tree/main/.github/ISSUE_TEMPLATE)
* added [PULL_REQUEST_TEMPLATE](https://github.com/obervinov/vault-package/tree/main/.github/PULL_REQUEST_TEMPLATE)
* added [CODEOWNERS](https://github.com/obervinov/vault-package/tree/main/.github/CODEOWNERS)
* added [dependabot.yml](https://github.com/obervinov/vault-package/tree/main/.github/dependabot.yml)


## v1.0.3 - 2023-02-03
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.0.2...v1.0.3 by @obervinov in https://github.com/obervinov/vault-package/pull/3 and https://github.com/obervinov/vault-package/pull/4
#### 🐛 Bug Fixes
* repeated fixed if condition for `secrets.kv.v2.configure`
#### 📚 Documentation
* updated documentation format in [README.md](https://github.com/obervinov/vault-package/blob/main/README.md)



## v1.0.2 - 2023-02-03
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.0.1...v1.0.2 by @obervinov in https://github.com/obervinov/vault-package/pull/2
#### 🚀 Features
* added [.flake8](https://github.com/obervinov/vault-package/blob/main/.flake8)
#### 🐛 Bug Fixes
* updated code format
* fixed if condition for `secrets.kv.v2.configure`
#### 📚 Documentation
* updated [README.md](https://github.com/obervinov/vault-package/blob/main/README.md)



## v1.0.1 - 2023-02-03
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.0.0...v1.0.1 by @obervinov in https://github.com/obervinov/vault-package/pull/1
#### 🐛 Bug Fixes
* added hvac=1.0.2 dependency in [setup.py](https://github.com/obervinov/vault-package/blob/main/setup.py)



## v1.0.0 - 2022-11-05
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/commits/v1.0.0
#### 💥 Breaking Changes
* **Module release**
