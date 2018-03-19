from .exceptions import *  # noqa
from .admin import *  # noqa
from .kernel import *  # noqa
from .vfolder import *  # noqa
from .request import *  # noqa

__all__ = [
    exceptions.__all__,  # noqa
    admin.__all__,  # noqa
    kernel.__all__,  # noqa
    vfolder.__all__,  # noqa
    request.__all__,  # noqa
]

__version__ = '1.3.0'


def get_user_agent():
    return 'Backend.AI Client for Python {0}'.format(__version__)
