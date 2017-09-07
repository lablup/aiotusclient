__all__ = [
    'BackendError',
    'BackendAPIError',
    'BackendClientError',
]


class BackendError(BaseException):
    '''Exception type to catch all ai.backend-related errors.'''
    pass


class BackendAPIError(BackendError):
    '''Exceptions returned by the API gateway.'''
    pass


class BackendClientError(BackendError):
    '''
    Exceptions from the client library, such as argument validation
    errors.
    '''
    pass
