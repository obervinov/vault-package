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
    version='2.0.1',
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
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development"
    ],
    keywords=['vault', 'client'],
    install_requires=[
        'hvac==1.1.0',
        'keyring==23.13.1',
        'python-dateutil==2.8.2',
        'logger @ git+https://github.com/obervinov/logger-package.git@v1.0.1',
    ]
)
