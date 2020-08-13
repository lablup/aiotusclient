# Backend.AI aiotusclient
Backend.AI aiotusclient is an tus client to communicate with tus server to manage vfolders used in Backend.AI client and other projects.

## Package Structure
* `ai.backend.aiotusclient`
  - `client`: The client instance class which communicates between Backend.AI Manager
  - `baseuploader and uploader`
    - Responsible for chunking the file and asynchronously uploading to tus server
  - `request`
    - Handles the uploading request

## Installation

### Prequisites
* Python 3.8 or higher with [pyenv](https://github.com/pyenv/pyenv)
and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) (optional but recommneded)

### Installation Process

First, prepare the source clone of this agent:
```console
# git clone https://github.com/lablup/aiotusclient
```

From now on, let's assume all shell commands are executed inside the virtualenv. And we located in backend.ai root directory.

Now install dependencies:
```console
# pip install -U aiotusclient
```


When done, import into your code the aiotusclient
```python
from aiotusclient import client

tus_client = client.TusClient(session_create_url, session_upload_url, rqst.headers, params)
```

### Reference
This library was forked from [tus-py-client](https://github.com/tus/tus-py-client) and customized in order to facilitate asynchronous communication with our TUS server.

