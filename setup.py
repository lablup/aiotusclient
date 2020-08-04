from setuptools import setup

setup(
   name='aiotusclient',
   version='1.0',
   description='Backend.AI aio tus client',
   author='Sergey Leksikov',
   author_email='sergey@lablup.com',
   install_requires=['asyncio', 'aiohttp', 'tqdm'] #external packages as dependencies
)