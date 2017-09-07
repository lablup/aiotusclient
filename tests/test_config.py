import pytest

from ai.backend.client.config import APIConfig, get_config, set_config


@pytest.fixture
def cfg_params():
    return {
        'endpoint': 'http://127.0.0.1:8081',
        'version': 'vtest',
        'user_agent': 'Backed.AI Client Test',
        'access_key': 'AKIAIOSFODNN7EXAMPLE',
        'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'hash_type': 'md5',
    }


def test_api_config_initialization(cfg_params):
    params = cfg_params
    cfg = APIConfig(**params)

    assert cfg.endpoint == params['endpoint']
    assert cfg.version == params['version']
    assert cfg.user_agent == params['user_agent']
    assert cfg.access_key == params['access_key']
    assert cfg.secret_key == params['secret_key']
    assert cfg.hash_type == params['hash_type']

    assert isinstance(cfg.endpoint, str)
    assert isinstance(cfg.version, str)
    assert isinstance(cfg.user_agent, str)
    assert isinstance(cfg.access_key, str)
    assert isinstance(cfg.secret_key, str)
    assert isinstance(cfg.hash_type, str)


def test_set_and_get_config(mocker, cfg_params):
    # Mocking the global variable ``_config``.
    # The value of a global variable will affect other test cases.
    mocker.patch('ai.backend.client.config._config', None)

    cfg = APIConfig(**cfg_params)
    set_config(cfg)

    assert get_config() == cfg


def test_access_and_secret_key_should_be_set_to_get_default_config(
        mocker, cfg_params):
    mocker.patch('ai.backend.client.config._config', None)

    # Neither SORNA_ACCESS_KEY nor SORNA_SECRET_KEY exists.
    mocker.patch('os.environ', {})
    with pytest.raises(KeyError) as e:
        get_config()
    err_key = str(e.value)
    assert 'SORNA_ACCESS_KEY' in err_key or 'SORNA_SECRET_KEY' in err_key

    # SORNA_ACCESS_KEY exists, but not SORNA_SECRET_KEY
    mocker.patch('os.environ', {'SORNA_ACCESS_KEY': cfg_params['access_key']})
    with pytest.raises(KeyError) as e:
        get_config()
    assert 'SORNA_SECRET_KEY' in str(e.value)

    # SORNA_SECRET_KEY exists, but not SORNA_ACCESS_KEY
    mocker.patch('os.environ', {'SORNA_SECRET_KEY': cfg_params['secret_key']})
    with pytest.raises(KeyError) as e:
        get_config()
    assert 'SORNA_ACCESS_KEY' in str(e.value)

    # Both keys exist. No exception should be raised.
    mocker.patch('os.environ', {
        'SORNA_ACCESS_KEY': cfg_params['access_key'],
        'SORNA_SECRET_KEY': cfg_params['secret_key']
    })
    get_config()


def test_get_config_return_default_config_when_config_is_none(
        mocker, cfg_params):
    mocker.patch('ai.backend.client.config._config', None)
    mocker.patch('os.environ', {
        'SORNA_ACCESS_KEY': cfg_params['access_key'],
        'SORNA_SECRET_KEY': cfg_params['secret_key']
    })

    cfg = get_config()
    for k, v in APIConfig.DEFAULTS.items():
        assert getattr(cfg, k) == v
