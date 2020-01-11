import sys

import click

from . import main
from .pretty import print_wait, print_done, print_error
from ..compat import asyncio_run
from ..session import Session, AsyncSession


@main.command()
@click.argument('session_id', metavar='SESSID')
def logs(session_id):
    '''
    Shows the output logs of a running container.

    \b
    SESSID: Session ID or its alias given when creating the session.
    '''
    with Session() as session:
        try:
            print_wait('Retrieving live container logs...')
            kernel = session.ComputeSession(session_id)
            result = kernel.get_logs().get('result')
            logs = result.get('logs') if 'logs' in result else ''
            print(logs)
            print_done('End of logs.')
        except Exception as e:
            print_error(e)
            sys.exit(1)


@main.command()
@click.argument('task_id', metavar='TASKID')
def task_logs(task_id):
    '''
    Shows the output logs of a batch task.

    \b
    TASKID: An UUID of a task (or kernel).
    '''
    async def _task_logs():
        async with AsyncSession() as session:
            async for chunk in session.ComputeSession.get_task_logs(task_id):
                print(chunk.decode('utf8', errors='replace'), end='')

    try:
        asyncio_run(_task_logs())
    except Exception as e:
        print_error(e)
        sys.exit(1)
