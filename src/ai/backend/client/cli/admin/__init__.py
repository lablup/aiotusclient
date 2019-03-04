from .. import main


@main.group()
def admin():
    '''
    Provides the admin API access.
    '''


def _attach_command():
    from . import (  # noqa
        agents, images, keypairs, resource_policies, sessions, vfolders
    )


_attach_command()
