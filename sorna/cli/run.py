import getpass
import sys
import traceback

from . import register_command
from .pretty import print_none, print_wait, print_done, print_fail
from ..kernel import Kernel
from ..compat import token_hex


@register_command
def run(args):
    '''Run the code.'''
    attach_to_existing = True
    if args.verbose:
        vprint_none = print_none
        vprint_wait = print_wait
        vprint_done = print_done
        vprint_fail = print_fail
    else:
        vprint_none = vprint_wait = lambda *args, **kwargs: None
        vprint_done = vprint_fail = lambda *args, **kwargs: None
    if not args.client_token:
        args.client_token = token_hex(16)
        attach_to_existing = False
        vprint_none('Client session token: {0}'.format(args.client_token))
        vprint_wait('Creating a temporary kernel...')
    else:
        vprint_none('Client session token: {0}'.format(args.client_token))
        vprint_wait('Connecting to the kernel...')
    kernel = Kernel.get_or_create(args.lang, args.client_token)
    vprint_done('Kernel (ID: {0}) is ready.'.format(kernel.kernel_id))

    try:
        if args.files:
            if args.code:
                print('You can run only either source files or command-line '
                      'code snippet.', file=sys.stderr)
                return
            vprint_wait('Uploading source files...')
            ret = kernel.upload(args.files)
            if ret.status // 100 != 2:
                print_fail('Uploading source files failed!')
                print('{0}: {1}\n{2}'.format(ret.status, ret.reason, ret.text()))
                return
            vprint_done('Uploading done.')
            #result = kernel.execute(mode='batch')
            #print(result)
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
    except:
        print_fail('Execution failed!')
        traceback.print_exc()
    finally:
        if not attach_to_existing:
            vprint_wait('Cleaning up the temporary kernel...')
            kernel.destroy()
            vprint_done('Cleaned up the kernel.')


run.add_argument('lang',
                 help='The runtime or programming language name')
run.add_argument('files', nargs='*',
                 help='The code file(s). Can be added multiple times')
run.add_argument('-t', '--client-token',
                 help='Attach to existing kernel using the given client-side '
                      'token [default: use a temporary kernel]')
run.add_argument('-c', '--code',
                 help='The code snippet in a single line.')
run.add_argument('-v', '--verbose', action='store_true', default=False,
                 help='Print execution details and status.')
