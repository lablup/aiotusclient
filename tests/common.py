from unittest import mock


def mock_coro(return_value):
    """
    Return mock coroutine.
    Python's default mock module does not support coroutines.
    """
    async def mock_coro(*args, **kargs):
        return return_value
    return mock.Mock(wraps=mock_coro)


class MockAsyncContextManager:
    """
    Mock async context manager.
    To get around `async with` statement for testing.
    Attributes can be set by passing `kwargs`.
    """
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        pass
