# Always prefer setuptools over distutils
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='sorna-client',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0',
    description='Sorna API Client Library',
    long_description='',
    url='https://github.com/lablup/sorna-client',
    author='Lablup Inc.',
    author_email='joongi@lablup.com',
    license='LGPL/BSD',

    packages=['sorna.client'],
    namespace_packages=['sorna'],

    install_requires=['aiohttp', 'namedlist', 'python-dateutil', 'simplejson'],
    extras_require={
        'dev': [],
        'test': ['pytest', 'pytest-mock'],
    },
    data_files=[],
)
