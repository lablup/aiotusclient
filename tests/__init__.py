from unittest import mock

from asynctest import CoroutineMock


class ContextMock(mock.Mock):

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class ContextMagicMock(mock.MagicMock):

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class ContextCoroutineMock(CoroutineMock):

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
