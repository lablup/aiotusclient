from setuptools import setup

setup(
   name='aiotusclient',
   version='1.0.0',
   description='Backend.AI aio tus client',
   author='Sergey Leksikov',
   author_email='sergey@lablup.com',
   packages=['aiotusclient'],
   install_requires=['asyncio', 'aiohttp', 'tqdm'] #external packages as dependencies
)