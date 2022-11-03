import pytest
from click.testing import CliRunner
from exunoplura import cli
from pathlib import Path
import json


@pytest.fixture
def fake_home_dir(monkeypatch, tmp_path):
    def fake_home():
        return tmp_path
    monkeypatch.setattr('pathlib.Path.home', fake_home)
    return tmp_path


def test_first_init(fake_home_dir):
    runner = CliRunner()
    result = runner.invoke(cli, 'init --server_name www.example.test')
    
    config_dir = fake_home_dir / '.exunoplura'
    location_conf_dir = config_dir / 'location_configs'
    central_conf = config_dir / 'exunoplura_nginx.conf'
    state_file = config_dir / 'state.json'

    assert config_dir.is_dir()
    assert location_conf_dir.is_dir()
    assert central_conf.is_file()
    assert state_file.is_file()
    central_conf_text = central_conf.read_text()
    assert 'server_name www.example.test;' in central_conf_text
    assert f'include {location_conf_dir}/*;' in central_conf_text
    state = json.loads(state_file.read_text())
    assert state == {'locations':[]}

def test_second_init(fake_home_dir):
    # fill the .exunoplura dir with a mock config
    config_dir = fake_home_dir / '.exunoplura'
    location_conf_dir = config_dir / 'location_configs'
    central_conf = config_dir / 'exunoplura_nginx.conf'
    location1_conf = location_conf_dir / 'location1.conf'
    location2_conf = location_conf_dir / 'location2.conf'
    state_file = config_dir / 'state.json'
    
    central_conf_text = 'server { some random; config entries; }'
    location1_conf_text = 'location { more random; config entries; }'
    location2_conf_text = 'location { even more; meaningless garble; }'
    state = {'some':'variable', 'locations':[{'more':'variables'}]}
    
    config_dir.mkdir()
    location_conf_dir.mkdir()
    central_conf.write_text(central_conf_text)
    location1_conf.write_text(location1_conf_text)
    location2_conf.write_text(location2_conf_text)
    state_file.write_text(json.dumps(state))

    test_first_init(fake_home_dir)
    
    # assert that the central config was overwritten
    assert central_conf.read_text() != central_conf_text
    # assert that location configs were not overwritten
    assert location1_conf.read_text() == location1_conf_text
    assert location2_conf.read_text() == location2_conf_text

def test_list(fake_home_dir):
    (fake_home_dir / '.exunoplura' / 'location_configs').mkdir(parents=True)
    runner = CliRunner()
    result = runner.invoke(cli, 'list')
    assert result.exit_code == 0
    assert '0 locations' in result.output
