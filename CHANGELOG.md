# Change Log
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).


## v2.1.0 - 2024-06-03
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v2.0.4...v2.1.0 by @obervinov in https://github.com/obervinov/vault-package/pull/47
#### 💥 Breaking Changes
* Changed environment variables
* Changed general class `VaultClient()` incoming parameters
* Decomposition of one overloaded class into several smaller classes responsible for their own aspect of interaction with vault.
#### 📚 Documentation
* Update `*.md` templates for issues and pull requests
#### 🚀 Features
* [cryptography NULL pointer dereference with pkcs12.serialize_key_and_certificates when called with a non-matching certificate and private key and an hmac_hash override ](https://github.com/obervinov/vault-package/security/dependabot/1)
* [Internationalized Domain Names in Applications (IDNA) vulnerable to denial of service from specially crafted inputs to idna.encode](https://github.com/obervinov/vault-package/security/dependabot/2)
* [Return `None` if the path does not exist when the `list_secrets()` method is called](https://github.com/obervinov/vault-package/issues/46)
* [Add delete() method in class](https://github.com/obervinov/vault-package/issues/38)
*


## v2.0.4 - 2024-02-07
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v2.0.3...v2.0.4 by @obervinov in https://github.com/obervinov/vault-package/pull/43
#### 🚀 Features
* Bump keyring from `23.13.1` to `24.3.0`


## v2.0.3 - 2024-02-04
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v2.0.2...v2.0.3 by @obervinov in https://github.com/obervinov/vault-package/pull/45
#### 🐛 Bug Fixes
* Fix support for `python 3.9`


## v2.0.2 - 2024-01-25
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v2.0.1...v2.0.2 by @obervinov in https://github.com/obervinov/vault-package/pull/42
#### 🐛 Bug Fixes
* [Fix badge with tests in README.md](https://github.com/obervinov/vault-package/issues/33)
* [Not working keyring for ubuntu secrets-tools](https://github.com/obervinov/vault-package/issues/30)
* [Fix the error that caused the workflow `create_release` to run twice - at pr/main](https://github.com/obervinov/vault-package/issues/37)
* [Add requirements dependency `dateutil`](https://github.com/obervinov/vault-package/issues/40)
* [Dependency graph does not work correctly, sort it out and fix it network/dependencies](https://github.com/obervinov/vault-package/issues/41)
#### 📚 Documentation
* [Add information about supported environment variables to the doc-string](https://github.com/obervinov/vault-package/issues/36)
* [Fix badge with tests in README.md](https://github.com/obervinov/vault-package/issues/33)
#### 🚀 Features
* [Merge all workflows to single file](https://github.com/obervinov/vault-package/issues/34)
* [Return None if secret path doesn't exist](https://github.com/obervinov/vault-package/issues/31)
* [Migration from pip to poetry](https://github.com/obervinov/vault-package/issues/23)
* [Add support for the environment variable `VAULT_MOUNT_POINT`](https://github.com/obervinov/vault-package/issues/35)


## v2.0.1 - 2023-06-20
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v2.0.0...v2.0.1 by @obervinov in https://github.com/obervinov/vault-package/pull/27
#### 🐛 Bug Fixes
* [Fix work with transit dependencies in setup.py](https://github.com/obervinov/vault-package/issues/26)
* [A bug with an infinite loop on the reissue of the token](https://github.com/obervinov/vault-package/issues/25)
* [Add dependencies between tasks in the GitHub Actions](https://github.com/obervinov/vault-package/issues/20)
* Fixed various typos in the code and doc-strings
#### 📚 Documentation
* [Add a description to the links in CHANGELOG.md](https://github.com/obervinov/vault-package/issues/28)
* [Add to README.md description of dependencies](https://github.com/obervinov/vault-package/issues/22)
#### 🚀 Features
* [Add automatic data saving of the newly generated approle to the system keystrore](https://github.com/obervinov/vault-package/issues/29)


## v2.0.0 - 2023-05-22
### What's Changed
**Full Changelog**: https://github.com/obervinov/vault-package/compare/v1.1.1...v2.0.0 by @obervinov in https://github.com/obervinov/vault-package/pull/10
#### 🐛 Bug Fixes
* [Fix: typos in workflow](https://github.com/obervinov/_templates/issues/16)
* [Fix: add the pylint module to install in the test.pylint.yml task](https://github.com/obervinov/_templates/issues/18)
* renamed the directory with modules: `src` -> `vault`
* removed condition `- '!main'` for [.github/workflows/tests.yml](https://github.com/obervinov/vault-package/blob/v2.0.0/.github/workflows/tests.yml#L3-L8) (this is done for the correct display of the badge in [README.md](https://github.com/obervinov/vault-package/blob/v2.0.0/README.md?plain=1#L4) on the `main` brunch)
#### 💥 Breaking Changes
**The new major version is completely incompatible with the old versions!**
* the `VaultClient()` class has been completely rewritten and refactored (all class methods and module logic have been changed).
* changed log format `f-string` -> `%s-lazzy`
* updated [SECURITY.md](https://github.com/obervinov/vault-package/blob/v2.0.0/SECURITY.md) policy
#### 🚀 Features
* [Add an automatic token reissue function to reduce lease_ttl](https://github.com/obervinov/vault-package/issues/16)
* [Add workflow with package installation verification (by tag, branch, default)](https://github.com/obervinov/vault-package/issues/14)
* [Add methods to automatically configure a new vault instance or prepare an existing instance](https://github.com/obervinov/vault-package/issues/12)
* all workflows migrated to version `v1.0.4`
* updated logger version `git = "https://github.com/obervinov/logger-package.git", tag = "v1.0.1"`
* added condition `paths: ['vault/**']` for `.github/workflows/release.yml` action (this is done so that you can update the documentation without creating an `PR` and a `new release`)
* added support for default environment variables: `VAULT_ADDR', `VAULT_TOKEN', `VAULT_APPROLE_ID` and `VAULT_APPROVED_SECRETID` for a more native and convenient way to interact with the vault api
* [Write tests for pytest](https://github.com/obervinov/vault-package/issues/19)
#### 📚 Documentation
* [Updated PR template: full changelog](https://github.com/obervinov/vault-package/issues/13)
* [Add to readme.md structure and rights to work with vault](https://github.com/obervinov/vault-package/issues/17)
* [Add to readme.md information about environment variables](https://github.com/obervinov/vault-package/issues/18)
* updated and expanded [README.md](https://github.com/obervinov/vault-package/tree/v2.0.0#-supported-environment-variables)
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
