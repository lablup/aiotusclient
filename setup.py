from setuptools import setup
from pathlib import Path
import re


setup_requires = [
    'setuptools>=46.1.0',
]

install_requires = [
    'aiohttp>=3.6.2',
    'tqdm>=4.42'
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
    python_requires='>=3.8',
    setup_requires=setup_requires,
    install_requires=install_requires,
)
