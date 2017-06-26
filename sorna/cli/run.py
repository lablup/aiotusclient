import sys
import getpass

from . import register_command
from ..kernel import Kernel
from ..compat import token_hex


@register_command
def run(args):
    '''Run the code.'''
    attach_to_existing = True
    vprint = print if args.verbose else lambda *args, **kwargs: None
    if not args.client_token:
        args.client_token = token_hex(16)
        attach_to_existing = False
        vprint('Creating temporary kernel '
               '(client-token: {0})'.format(args.client_token))
    kernel = Kernel.get_or_create(args.lang, args.client_token)
    vprint('Connected to kernel (id: {0})'.format(kernel.kernel_id))

    if args.file:
        if args.code:
            print('You can run only either source files or command-line '
                  'code snippet.', file=sys.stderr)
            return
        # upload files
        kernel.upload(args.file)
        # run code
        result = kernel.execute(mode='batch')
        print(result)
    else:
        if not args.code:
            print('You should provide the command-line code snippet using '
                  '"-c" option if run without files.', file=sys.stderr)
            return
        # run code
        while True:
            result = kernel.execute(args.code, mode='query')
            for rec in result['console']:
                if rec[0] == 'stdout':
                    print(rec[1], end='', file=sys.stdout)
                elif rec[0] == 'stderr':
                    print(rec[1], end='', file=sys.stderr)
                else:
                    print('----- output record (type: {0}) -----'.format(rec[0]))
                    print(rec[1])
                    print('----- end of record -----')
            sys.stdout.flush()
            if result['status'] == 'finished':
                break
            elif result['status'] == 'waiting-input':
                if result['options'].get('is_password', False):
                    args.code = getpass.getpass()
                else:
                    args.code = input()
            elif result['status'] == 'continued':
                continue

    if not attach_to_existing:
        kernel.destroy()
        vprint('Destroyed kernel '
               '(client-token: {0}).'.format(args.client_token))


run.add_argument('lang',
                 help='The runtime or programming language name')
run.add_argument('file', nargs='*',
                 help='The code file(s). Can be added multiple times')
run.add_argument('-t', '--client-token',
                 help='Attach to existing kernel using the given client-side '
                      'token [default: use a temporary kernel]')
run.add_argument('-c', '--code',
                 help='The code snippet in a single line.')
run.add_argument('-v', '--verbose', action='store_true', default=False,
                 help='Print execution details and status.')
