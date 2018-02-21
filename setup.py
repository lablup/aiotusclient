from setuptools import setup
from pathlib import Path
import re

install_requires = [
    'colorama',
    'multidict',
    'aiohttp~=3.0.1',
    'async_timeout',
    'namedlist>=1.6',
    'python-dateutil>=2.5',
    'requests>=2.12',
    'ConfigArgParse==0.12.0',
    'tabulate>=0.7.7',
    'humanize',
]
dev_requires = [
]
ci_requires = [
    'wheel',
    'twine',
]
test_requires = [
    'pytest>=3.4',
    'pytest-cov',
    'pytest-mock',
    'pytest-asyncio',
    'pytest-sugar',
    'asynctest',
    'codecov',
    'flake8',
]


def read_src_version():
    path = Path(__file__).parent / 'ai' / 'backend' / 'client' / '__init__.py'
    src = path.read_text()
    m = re.search(r"^__version__ = '([^']+)'$", src, re.MULTILINE)
    assert m is not None, 'Could not read the version information!'
    return m.group(1)


setup(
    name='backend.ai-client',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=read_src_version(),
    description='Backend.AI Client for Python',
    long_description=Path('README.rst').read_text(),
    url='https://github.com/lablup/backend.ai-client-py',
    author='Lablup Inc.',
    author_email='joongi@lablup.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ],
    packages=[
        'ai.backend.client',
        'ai.backend.client.asyncio',
        'ai.backend.client.cli',
        'ai.backend.client.cli.admin',
    ],
    python_requires='>=3.5',
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires + ci_requires + test_requires,
        'test': test_requires,
        'ci': ci_requires + test_requires,
    },
    data_files=[],
    entry_points={
        'console_scripts': [
            'backend.ai = ai.backend.client.cli:main',
            'lcc = ai.backend.client.cli:main',
            'lpython = ai.backend.client.cli:main',
        ],
    },
)
