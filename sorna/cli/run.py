from . import register_command


@register_command
def run(args):
    '''Run the code.'''
    pass


run.add_argument('lang',
                 help='The runtime or programming language name')
