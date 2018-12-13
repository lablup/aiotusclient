import click

from .pretty import print_fail


# def main():

#     import ai.backend.client.cli.config # noqa
#     import ai.backend.client.cli.run    # noqa
#     import ai.backend.client.cli.proxy  # noqa
#     import ai.backend.client.cli.admin  # noqa
#     import ai.backend.client.cli.admin.keypairs  # noqa
#     import ai.backend.client.cli.admin.sessions  # noqa
#     import ai.backend.client.cli.admin.agents    # noqa
#     import ai.backend.client.cli.admin.vfolders  # noqa
#     import ai.backend.client.cli.manager  # noqa
#     import ai.backend.client.cli.vfolder # noqa
#     import ai.backend.client.cli.ps     # noqa
#     import ai.backend.client.cli.logs   # noqa
#     import ai.backend.client.cli.files           # noqa
#     import ai.backend.client.cli.app  # noqa

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


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


def _attach_command():
    from .admin import admin        # noqa
    from .config import config      # noqa
    from .app import app            # noqa
    from .files import upload, download, ls     # noqa
    from .logs import logs          # noqa
    from .manager import manager    # noqa
    from .proxy import proxy        # noqa
    from .ps import ps              # noqa
    from .vfolder import vfolder    # noqa

    main.add_command(admin)
    main.add_command(config)
    main.add_command(app)
    main.add_command(upload)
    main.add_command(download)
    main.add_command(ls)
    main.add_command(logs)
    main.add_command(manager)
    main.add_command(proxy)
    main.add_command(ps)
    main.add_command(vfolder)


_attach_command()
