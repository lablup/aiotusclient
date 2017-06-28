class SornaError(BaseException):
    '''Exception type to catch all Sorna-related errors.'''
    pass


class SornaAPIError(SornaError):
    '''Exceptions returned by the API gateway.'''
    pass


class SornaClientError(SornaError):
    '''
    Exceptions from the client library, such as argument validation
    errors.
    '''
    pass
