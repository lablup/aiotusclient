import argparse
import functools
from pathlib import Path
import sys
from typing import Callable, Optional, Union

import colorama
import configargparse

from .pretty import print_fail

ArgParserType = Union[argparse.ArgumentParser, configargparse.ArgumentParser]

global_argparser = configargparse.ArgumentParser(
    prog='backend.ai',
    description='Backend.AI command line interface')
_subparsers = dict()


def register_command(handler: Callable[[argparse.Namespace], None],
                     main_parser: Optional[ArgParserType]=None,
                    ) -> Callable[[argparse.Namespace], None]:  # noqa
    if main_parser is None:
        main_parser = global_argparser
    if id(main_parser) not in _subparsers:
        subparsers = main_parser.add_subparsers(title='commands',
                                                dest='command')
        _subparsers[id(main_parser)] = subparsers
    else:
        subparsers = _subparsers[id(main_parser)]

    @functools.wraps(handler)
    def wrapped(args):
        handler(args)

    doc_summary = handler.__doc__.split('\n\n')[0]
    inner_parser = subparsers.add_parser(handler.__name__.replace('_', '-'),
                                         description=handler.__doc__,
                                         help=doc_summary)
    inner_parser.set_defaults(function=wrapped)
    wrapped.register_command = functools.partial(register_command,
                                                 main_parser=inner_parser)
    wrapped.add_argument = inner_parser.add_argument
    return wrapped


@register_command
def help(args):
    '''
    Shows the help.
    '''
    global_argparser.print_help()


def main():

    colorama.init()

    import ai.backend.client.cli.config # noqa
    import ai.backend.client.cli.run    # noqa
    import ai.backend.client.cli.proxy  # noqa
    import ai.backend.client.cli.admin  # noqa
    import ai.backend.client.cli.admin.keypairs  # noqa
    import ai.backend.client.cli.admin.sessions  # noqa
    import ai.backend.client.cli.admin.agents    # noqa
    import ai.backend.client.cli.admin.vfolders  # noqa
    import ai.backend.client.cli.vfolder # noqa
    import ai.backend.client.cli.ps     # noqa
    import ai.backend.client.cli.logs   # noqa

    if len(sys.argv) <= 1:
        global_argparser.print_help()
        return

    mode = Path(sys.argv[0]).stem

    if mode == '__main__':
        pass
    elif mode == 'lcc':
        sys.argv.insert(1, 'c')
        sys.argv.insert(1, 'run')
    elif mode == 'lpython':
        sys.argv.insert(1, 'python')
        sys.argv.insert(1, 'run')

    args = global_argparser.parse_args()
    if hasattr(args, 'function'):
        args.function(args)
    else:
        print_fail('The command is not specified or unrecognized.')
