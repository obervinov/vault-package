"""
This module is necessary to distribute and install the written module via pip
"""
from setuptools import setup

with open('README.md', 'r', encoding='utf8') as readme:
    readme_content = readme.read()
with open('CHANGELOG.md', 'r', encoding='utf8') as changelog:
    changelog_content = changelog.read()

setup(
    name='vault',
    version='2.0.0',
    license='MIT',
    description=(
        "This is an additional implementation compared to the hvac module. "
        "The main purpose of which is to simplify the use "
        "and interaction with vault for my standard projects. "
        "This module contains a set of methods for working with secrets "
        "and quickly configuring Vault."
    ),
    py_modules=['vault'],
    package_dir={'': 'vault'},
    author='Oleg Bervinov',
    author_email='obervinov@pm.me',
    long_description=(f"{readme_content}""\n\n"f"{changelog_content}"),
    long_description_content_type="text/markdown",
    url='https://github.com/obervinov/vault-package',
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent'
    ],
    keywords=['vault', 'client'],
    install_requires=[
        'hvac==1.1.0'
        'keyring==23.13.1'
    ],
    dependency_links=[
        'https://github.com/obervinov/logger-package/tarball/master#egg=logger-1.0.1'
    ]
)
