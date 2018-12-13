import click

from .pretty import print_fail


class AliasGroup(click.Group):
    """
    Enable command aliases.

    ref) https://github.com/click-contrib/click-aliases
    """
    def __init__(self, *args, **kwargs):
        super(AliasGroup, self).__init__(*args, **kwargs)
        self._commands = {}
        self._aliases = {}

    def command(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super(AliasGroup, self).command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd
        return _decorator

    def group(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super(AliasGroup, self).group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd
        return _decorator

    def get_command(self, ctx, cmd_name):
        if cmd_name in self._aliases:
            cmd_name = self._aliases[cmd_name]
        command = super(AliasGroup, self).get_command(ctx, cmd_name)
        if command:
            return command

    def format_commands(self, ctx, formatter):
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command. Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue
            if subcommand in self._commands:
                aliases = ','.join(sorted(self._commands[subcommand]))
                subcommand = '{0} ({1})'.format(subcommand, aliases)
            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)
            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand, help))
            if rows:
                with formatter.section('Commands'):
                    formatter.write_dl(rows)


# def main():

#     if len(sys.argv) <= 1:
#         global_argparser.print_help()
#         return

#     mode = Path(sys.argv[0]).stem

#     if mode == '__main__':
#         pass
#     elif mode == 'lcc':
#         sys.argv.insert(1, 'c')
#         sys.argv.insert(1, 'run')
#     elif mode == 'lpython':
#         sys.argv.insert(1, 'python')
#         sys.argv.insert(1, 'run')

#     args = global_argparser.parse_args()
#     if hasattr(args, 'function'):
#         args.function(args)
#     else:
#         print_fail('The command is not specified or unrecognized.')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(cls=AliasGroup, invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.pass_context
def main(ctx):
    """Backend.AI command line interface.
    """
    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


def _attach_command():
    from . import admin, config, app, files, logs, manager, proxy, ps, run, vfolder


_attach_command()
