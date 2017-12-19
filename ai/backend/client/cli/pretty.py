import enum
import functools
import sys
import textwrap

__all__ = (
    'PrintStatus', 'print_pretty', 'print_info', 'print_wait',
    'print_done', 'print_fail',
)


class PrintStatus(enum.Enum):
    NONE = 0
    WAITING = 1
    DONE = 2
    FAILED = 3


def print_pretty(msg, *, status=PrintStatus.NONE, file=None):
    if file is None:
        file = sys.stderr
    if status == PrintStatus.NONE:
        indicator = '\x1b[96m\u2219' if file.isatty() else '\u2219'
    elif status == PrintStatus.WAITING:
        assert '\n' not in msg, 'Waiting message must be a single line.'
        indicator = '\x1b[93m\u22EF' if file.isatty() else '\u22EF'
    elif status == PrintStatus.DONE:
        indicator = '\x1b[92m\u2714' if file.isatty() else '\u2714'
    elif status == PrintStatus.FAILED:
        indicator = '\x1b[91m\u2718' if file.isatty() else '\u2718'
    else:
        raise ValueError
    if file.isatty():
        print('\x1b[2K', end='', file=file)
    text = textwrap.indent(msg, '  ')
    text = indicator + text[1:]
    if file.isatty():
        text += '\x1b[0m'
    print('{0}\r'.format(text), end='', file=file)
    file.flush()
    if status != PrintStatus.WAITING:
        print('', file=file)


print_info = functools.partial(print_pretty, status=PrintStatus.NONE)
print_wait = functools.partial(print_pretty, status=PrintStatus.WAITING)
print_done = functools.partial(print_pretty, status=PrintStatus.DONE)
print_fail = functools.partial(print_pretty, status=PrintStatus.FAILED)
