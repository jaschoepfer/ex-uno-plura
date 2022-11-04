import pytest
from click.testing import CliRunner
from pathlib import Path
import json

from exunoplura import cli
import paths
import state

@pytest.fixture
def fake_home_dir(monkeypatch, tmp_path):
    def fake_home():
        return tmp_path
    monkeypatch.setattr('pathlib.Path.home', fake_home)
    return tmp_path


def test_first_init(fake_home_dir):
    runner = CliRunner()
    
    result = runner.invoke(cli, 'init --server_name www.example.test')
    
    assert result.exit_code == 0
    assert paths.config_dir().is_dir()
    assert paths.location_conf_dir().is_dir()
    assert paths.central_conf().is_file()
    assert paths.state_file().is_file()
    central_conf_text = paths.central_conf().read_text()
    assert 'server_name www.example.test;' in central_conf_text
    assert f'include { paths.location_conf_dir() }/*;' in central_conf_text
    assert state.read() == { 'locations': [] }

def test_second_init(fake_home_dir):
    # fill the .exunoplura dir with a mock config
    location1_conf = paths.location_conf_dir() / 'location1.conf'
    location2_conf = paths.location_conf_dir() / 'location2.conf'
    
    central_conf_text = 'server { some random; config entries; }'
    location1_conf_text = 'location { more random; config entries; }'
    location2_conf_text = 'location { even more; meaningless garble; }'
    _state = {'some':'variable', 'locations':[{'more':'variables'}]}
    
    paths.config_dir().mkdir()
    paths.location_conf_dir().mkdir()
    paths.central_conf().write_text(central_conf_text)
    location1_conf.write_text(location1_conf_text)
    location2_conf.write_text(location2_conf_text)
    state.write(_state)

    test_first_init(fake_home_dir)
    
    # assert that the central config was overwritten
    assert paths.central_conf().read_text() != central_conf_text
    # assert that location configs were not overwritten
    assert location1_conf.read_text() == location1_conf_text
    assert location2_conf.read_text() == location2_conf_text

def test_list(fake_home_dir):
    runner = CliRunner()
    runner.invoke(cli, 'init')
    
    result = runner.invoke(cli, 'list')

    assert result.exit_code == 0
    assert '0 locations' in result.output

def test_create(fake_home_dir):
    runner = CliRunner()
    runner.invoke(cli, 'init')
    name = 'test_name'
    port = 8008

    result = runner.invoke(cli, ['create', name, str(port)])

    assert result.exit_code == 0
    new_loc = { 'name': name, 'http-port': port }
    assert any(l == new_loc for l in state.get_locations())
    new_conf = paths.location_conf_dir() / f'{ name }.conf'
    assert new_conf.is_file()
    new_conf_text = new_conf.read_text()
    assert f'location /{ name }' in new_conf_text
    assert f'proxy_pass http://localhost:{ port }/' in new_conf_text

