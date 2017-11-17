from . import register_command
from ..vfolder import VFolder


@register_command
def vfolder(args):
    '''Provides virtual folder operations.'''
    print('Run with -h/--help for usage.')


@vfolder.register_command
def list(args):
    '''List virtual folders that belongs to the current user.'''
    data = VFolder.list()
    print(data)


@vfolder.register_command
def create(args):
    '''Create a new virtual folder.'''
    result = VFolder.create(args.name)
    print(result)


create.add_argument('name', type=str, help='The name of a virtual folder.')


@vfolder.register_command
def delete(args):
    '''Delete the given virtual folder. This operation is irreversible!'''
    VFolder(args.name).delete()


delete.add_argument('name', type=str, help='The name of a virtual folder.')


@vfolder.register_command
def info(args):
    '''Show the information of the given virtual folder.'''
    result = VFolder(args.name).info()
    print(result)


info.add_argument('name', type=str, help='The name of a virtual folder.')


@vfolder.register_command
def upload(args):
    '''Upload a file to the virtual folder.'''
    result = VFolder(args.name).upload(args.filename)
    print(result.status)


upload.add_argument('name', type=str, help='The name of a virtual folder.')
upload.add_argument('filename', type=str, help='Path to the uploaded file.')
