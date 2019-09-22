import getpass
import json
import sys

import click

from . import main
from .pretty import print_done, print_error, print_fail, print_warn
from .. import __version__
from ..config import get_config, local_state_path
from ..session import Session


@main.command()
def config():
    '''
    Shows the current configuration.
    '''
    config = get_config()
    print('Client version: {0}'.format(click.style(__version__, bold=True)))
    print('API endpoint: {0} ({1})'.format(
          click.style(str(config.endpoint), bold=True),
          click.style(str(config.endpoint_type), fg='cyan', bold=True)))
    print('API version: {0}'.format(click.style(config.version, bold=True)))
    if config.domain:
        print('Domain name: "{0}"'.format(click.style(config.domain, bold=True)))
    if config.group:
        print('Group name: "{0}"'.format(click.style(config.group, bold=True)))
    if config.is_anonymous:
        print('Access key: (this is an anonymous session)')
    elif config.endpoint_type == 'docker':
        pass
    elif config.endpoint_type == 'session':
        if (local_state_path / 'cookie.dat').exists() and \
                (local_state_path / 'config.json').exists():
            sess_config = json.loads((local_state_path / 'config.json').read_text())
            print('Username: "{0}"'.format(click.style(sess_config.get('username', ''), bold=True)))
    else:
        print('Access key: "{0}"'.format(click.style(config.access_key, bold=True)))
        masked_skey = config.secret_key[:6] + ('*' * 24) + config.secret_key[-10:]
        print('Secret key: "{0}"'.format(click.style(masked_skey, bold=True)))
    print('Signature hash type: {0}'.format(
        click.style(config.hash_type, bold=True)))
    print('Skip SSL certificate validation? {0}'.format(
        click.style(str(config.skip_sslcert_validation), bold=True)))


@main.command()
def login():
    '''
    Log-in to the console API proxy.
    It stores the current session cookie in the OS-default
    local application data location.
    '''
    user_id = input('User ID: ')
    password = getpass.getpass()

    config = get_config()
    if config.endpoint_type != 'session':
        print_warn('To use login, your endpoint type must be "session".')
        raise click.Abort()

    with Session() as session:
        try:
            result = session.Auth.login(user_id, password)
            if not result['authenticated']:
                print_fail('Login failed.')
                sys.exit(1)
            print_done('Login succeeded.')

            local_state_path.mkdir(parents=True, exist_ok=True)
            session.aiohttp_session.cookie_jar.update_cookies(result['cookies'])
            session.aiohttp_session.cookie_jar.save(local_state_path / 'cookie.dat')
            (local_state_path / 'config.json').write_text(json.dumps(result.get('config', {})))
        except Exception as e:
            print_error(e)


@main.command()
def logout():
    '''
    Log-out from the console API proxy and clears the local cookie data.
    '''
    config = get_config()
    if config.endpoint_type != 'session':
        print_warn('To use logout, your endpoint type must be "session".')
        raise click.Abort()

    with Session() as session:
        try:
            session.Auth.logout()
            print_done('Logout done.')
            try:
                (local_state_path / 'cookie.dat').unlink()
                (local_state_path / 'config.json').unlink()
            except (IOError, PermissionError):
                pass
        except Exception as e:
            print_error(e)
