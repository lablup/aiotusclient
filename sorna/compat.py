'''
A compatibility module for backported codes from Python 3.6 standard library.
'''

import binascii
import os
import sys
import types


def token_bytes(nbytes=None):
    '''
    Emulation of secrets.token_bytes()
    '''
    if nbytes is None:
        nbytes = 32
    return os.urandom(nbytes)


def token_hex(nbytes=None):
    '''
    Emulation of secrets.token_hex()
    '''
    return binascii.hexlify(token_bytes(nbytes)).decode('ascii')


class Py36Type(type):
    '''
    Emulation of PEP-487.
    (ref: https://www.python.org/dev/peps/pep-0487/)
    '''

    def __new__(cls, *args, **kwargs):
        if len(args) != 3:
            return super().__new__(cls, *args)
        name, bases, ns = args
        init = ns.get('__init_subclass__')
        if isinstance(init, types.FunctionType):
            ns['__init_subclass__'] = classmethod(init)
        self = super().__new__(cls, name, bases, ns)
        for k, v in self.__dict__.items():
            func = getattr(v, '__set_name__', None)
            if func is not None:
                func(self, k)
        if hasattr(super(self, self), '__init_subclass__'):
            super(self, self).__init_subclass__(**kwargs)
        return self

    def __init__(self, name, bases, ns, **kwargs):
        super().__init__(name, bases, ns)


class Py36Object(object, metaclass=Py36Type):
    @classmethod
    def __init_subclass__(cls):
        pass


if sys.version_info >= (3, 6):
    Py36Object = object  # noqa
