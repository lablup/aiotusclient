import sys

import pytest

from ai.backend.client.cli import main
from ai.backend.client.config import get_config
from ai.backend.client.kernel import Kernel
# from ai.backend.client.cli.run import run


@pytest.mark.parametrize('cmd', ['-h', '--help', 'help'])
def test_print_help(cmd, capsys, mocker):
    mocker.patch.object(sys, 'argv', ['backend.ai', cmd])
    try:
        main()
    except SystemExit:
        pass
    out, _ = capsys.readouterr()
    assert 'usage: backend.ai' in out


def test_config(capsys, mocker):
    mocker.patch.object(sys, 'argv', ['backend.ai', 'config'])
    config = get_config()
    main()
    out, _ = capsys.readouterr()
    assert config.endpoint in out
    assert config.version in out
    assert config.access_key in out
    assert config.secret_key[:6] in out
    assert config.hash_type in out


def test_compiler_shortcut(mocker):
    mocker.patch.object(sys, 'argv', ['lcc', '-h'])
    try:
        main()
    except SystemExit:
        pass
    assert sys.argv == ['lcc', 'run', 'c', '-h']

    mocker.patch.object(sys, 'argv', ['lpython', '-h'])
    try:
        main()
    except SystemExit:
        pass
    assert sys.argv == ['lpython', 'run', 'python', '-h']


class TestRunCommand:
    def test_either_code_or_file_is_required(self, capsys, mocker):
        fake_get_or_create = mocker.MagicMock()
        mocker.patch.object(Kernel, 'get_or_create', fake_get_or_create)
        mocker.patch.object(sys, 'argv', ['backend.ai', 'run', 'python'])

        main()
        _, err = capsys.readouterr()
        assert 'provide the command-line code snippet using "-c"' in err
