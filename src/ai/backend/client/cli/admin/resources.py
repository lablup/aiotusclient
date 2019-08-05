import sys

import click
from tabulate import tabulate

from . import admin
from ...session import Session
from ..pretty import print_error, print_fail


@admin.group()
def resources():
    '''
    Manage resources.
    (admin privilege required)
    '''


@resources.command()
def resource_slots():
    """
    Get available resource slots.
    """
    with Session() as session:
        ret = session.Resource.get_resource_slots()
        for key, value in ret.items():
            print(key, '(' + value + ')')


@resources.command()
def vfolder_types():
    """
    Get available vfolder types.
    """
    with Session() as session:
        ret = session.Resource.get_vfolder_types()
        for t in ret:
            print(t)


@resources.command()
def recalculate_usage():
    """
    Re-calculate resource occupation by sessions.

    Sometime, reported allocated resources is deviated from the actual value.
    By executing this command, the discrepancy will be corrected with real value.
    """
    with Session() as session:
        session.Resource.recalculate_usage()
    print('Resource allocation is re-calculated.')
