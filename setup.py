from setuptools import setup

setup(
    name = 'vault', 
    version = '1.0.1',
    description = 'This module contains a collection of methods for working with vault.',
    py_modules = ["vault"],
    package_dir = {'':'src'},
    author = 'Oleg Bervinov',
    author_email = 'obervinov@mail.ru',
    long_description = open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
    long_description_content_type = "text/markdown",
    url='https://github.com/obervinov/vault-package',
    include_package_data=True,
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: BSD License",
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Text Processing',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
    ],
    keywords = ['vault', 'secure'],
    install_requires=[
            'hvac',
    ],
)