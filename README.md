Sorna Client
============

[![Travis Build Status](https://travis-ci.org/lablup/sorna-client.svg?branch=master)](https://travis-ci.org/lablup/sorna-client)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/5h6r1cmbx2965yn1/branch/master?svg=true)](https://ci.appveyor.com/project/achimnol/sorna-client/branch/master)
[![Code Coverage](https://codecov.io/gh/lablup/sorna-client/branch/master/graph/badge.svg)](https://codecov.io/gh/lablup/sorna-client)
[![PyPI](https://badge.fury.io/py/sorna-client.svg)](https://pypi.python.org/pypi/sorna-client)

The API client library for [Sorna](http://sorna.io)

Usage
-----

Grab your keypair from [cloud.sorna.io](https://cloud.sorna.io) or your cluster admin.

```sh
export SORNA_ACCESS_KEY=...
export SORNA_SECRET_KEY=...

# optional (for local clusters)
export SORNA_ENDPOINT="https://my-precious-cluster/"
```

Synchronous API
---------------

```python
from sorna.kernel import Kernel

kern = Kernel.get_or_create('lua5', client_token='abc')
result = kern.execute('print("hello world")', mode='query')
print(result['console'])
kern.destroy()
```

Asynchronous API
----------------

```python
import asyncio
from sorna.asyncio.kernel import AsyncKernel

async def main():
    kern = await AsyncKernel.get_or_create('lua5', client_token='abc')
    result = await kern.execute('print("hello world")', mode='query')
    print(result['console'])
    await kern.destroy()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()
```
