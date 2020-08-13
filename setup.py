from setuptools import setup, find_namespace_packages
from typing import List

setup_requires = [
    'setuptools>=46.1.0',
]

install_requires = [
    'aiohttp~=3.6.2',
    'tqdm~=4.42'
]

setup(
    name='aiotusclient',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.0',
    description='Backend.AI aiotusclient for Python',
    url='https://github.com/lablup/aiotusclient',
    author='Lablup Inc.',
    author_email='sergey@lablup.com',
    license='MIT',
    packages=['aiotusclient'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ],

    python_requires='>=3.8',
    setup_requires=setup_requires,
    install_requires=install_requires
)
