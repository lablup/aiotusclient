from setuptools import setup
from pathlib import Path
import re


setup_requires = [
    'setuptools>=49.6.0',
]

install_requires = [
    'aiohttp>=3.6.2',
    'tqdm>=4.42'
]
build_requires = [
    'wheel>=0.35.1',
    'twine>=3.1.1',
    'towncrier>=19.2.0',
]
test_requires = [
    'pytest~=6.0.1',
    'pytest-cov',
    'pytest-mock',
    'pytest-asyncio>=0.14.0',
    'aioresponses~=0.6.3',
    'codecov',
]
lint_requires = [
    'flake8>=3.8.1',
]
typecheck_requires = [
    'mypy>=0.782',
]


def get_version():
    src = (Path(__file__).parent / 'aiotusclient' / '__init__.py').read_text()
    m = re.search(r"""^__version__\s*=\s*(["'])([^'"]+)\1$""", src)
    return m.group(2)


setup(
    name='aiotusclient',
    version=get_version(),
    description='tus.io-compatible upload client library for Python asyncio',
    url='https://github.com/lablup/aiotusclient',
    author='Lablup Inc.',
    author_email='sergey@lablup.com',
    license='MIT',
    packages=['aiotusclient'],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
    python_requires='>=3.7',
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require={
        'build': build_requires,
        'test': test_requires,
        'lint': lint_requires,
        'typecheck': typecheck_requires,
    },
)
