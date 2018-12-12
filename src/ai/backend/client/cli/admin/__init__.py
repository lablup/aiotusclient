import click


@click.group()
def admin():
    '''
    Provides the admin API access.
    '''


def _attach_command():
    from .agents import agent, agents               # noqa
    from .keypairs import keypair, keypairs, add    # noqa
    from .sessions import sessions, session         # noqa
    from .vfolders import vfolders                  # noqa

    admin.add_command(agent)
    admin.add_command(agents)
    admin.add_command(keypair)
    admin.add_command(keypairs)
    admin.add_command(add)
    admin.add_command(session)
    admin.add_command(sessions)
    admin.add_command(vfolders)


_attach_command()
