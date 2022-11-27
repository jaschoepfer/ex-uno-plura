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
    server_name = 'example.url'
    
    result = runner.invoke(cli, f'init --server_name { server_name }')
    
    assert result.exit_code == 0
    assert paths.central_conf().read_text() == f'''server {{
	listen 80;
	listen [::]:80;

	server_name { server_name };

	# load location blocks
	include { paths.location_conf_dir() }/*;
}}
'''
    assert state.read() == { 'locations': [] }

def test_create(fake_home_dir):
    runner = CliRunner()
    runner.invoke(cli, 'init')
    name = 'test_name'
    port = 8008

    result = runner.invoke(cli, ['create', name, str(port)])

    assert result.exit_code == 0
    assert state.read() == { 'locations': [{ 'name': name, 'http-port': port }] }
    assert (paths.location_conf_dir() / f'{ name }.conf').read_text() == f'''location /{ name } {{
	proxy_pass http://localhost:{ port }/;
}}
'''

