import pytest
from click.testing import CliRunner
from pathlib import Path
import json

from exunoplura import cli
import paths

@pytest.fixture
def fake_home_dir(monkeypatch, tmp_path):
    def fake_home():
        return tmp_path
    monkeypatch.setattr('pathlib.Path.home', fake_home)
    return tmp_path


def test_create_server(fake_home_dir):
    runner = CliRunner()
    name = 'example.url'

    result = runner.invoke(cli, f'create-server { name }')
 
    assert result.exit_code == 0
    server_dir = paths.server_dir(name)
    assert paths.server_conf(name).read_text() == f'''server {{
    server_name { name };
    listen 80;
    listen [::]:80;

    # load directories
    include { server_dir }/*;
}}
'''

def test_create_ssl_server(fake_home_dir):
    runner = CliRunner()
    name = 'example.url'
    cert = fake_home_dir / 'cert.pem'
    key = fake_home_dir / 'key.pem'
    # tool checks for file existance
    cert.touch()
    key.touch()

    result = runner.invoke(cli, f'create-server --cert { cert } --key { key } { name }')

    assert result.exit_code == 0
    server_dir = paths.server_dir(name)
    assert paths.server_conf(name).read_text() == f'''server {{
    server_name { name };
    listen 80;
    listen [::]:80;

    listen 443 ssl;
    listen [::]:443 ssl;
    ssl_certificate { cert };
    ssl_certificate_key { key };

    # load directories
    include { server_dir }/*;
}}
'''

def test_create_dir(fake_home_dir):
    runner = CliRunner()
    server = 'example.url'
    runner.invoke(cli, f'create-server { server }')
    path = '/directory'
    port = 5050

    result = runner.invoke(cli, f'create-dir --proxy-port { port } { server } { path }')

    assert result.exit_code == 0
    assert paths.dir_conf(server, path).read_text() == f'''location /directory {{

    proxy_pass http://localhost:5050/;

}}
'''

