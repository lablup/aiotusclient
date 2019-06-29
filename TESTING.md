Testing Guide
=============

Unit Tests
----------

Unit tests performs function-by-function tests to ensure their individual
functionality.

### Hot to run

```console
python -m pytest -m 'not integration' tests
```


Integration Tests
-----------------

Integration tests actually makes API requests to a running gateway server
to test the full functionality of the client as well as the manager.

They are marked as "integration" using the `@pytest.mark.integration` decorator
to each test case.

### Prerequisite

The gateway must be running at http://localhost:8081 to execute this test
suite.  The gateway server must have at least one agent.

Please refer the README of the manager and agent repositories to set up them.
To avoid an indefinite waiting time for pulling Docker images:
* (manager) `python -m ai.backend.manager.cli etcd rescan-images`
* (agent) `docker pull ...`
  - `lablup/python:3.6-ubuntu18.04`
  - `lablup/lua:5.3-alpine3.8`

**TIP:** The *halfstack* configuration is compatible with this integration test suite.

And execute both the gateway and the agent:
```console
$ python -m ai.backend.client.gateway.server
$ python -m ai.backend.client.agent.server
```

### How to run

```console
python -m pytest -m 'integration' tests
```
