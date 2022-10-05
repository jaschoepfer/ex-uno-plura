import pytest
from click.testing import CliRunner
from exunoplura import cli
from pathlib import Path


@pytest.fixture
def fake_home_dir(monkeypatch, tmp_path):
    def fake_home():
        return tmp_path
    monkeypatch.setattr('pathlib.Path.home', fake_home)
    return tmp_path


def test_first_init(fake_home_dir):
    runner = CliRunner()
    result = runner.invoke(cli, 'init --servername www.example.test')
    
    config_dir = fake_home_dir / '.exunoplura'
    sandbox_conf_dir = config_dir / 'sandbox_configs'
    central_conf = config_dir / 'exunoplura.conf'

    assert config_dir.is_dir()
    assert sandbox_conf_dir.is_dir()
    assert central_conf.is_file()
    central_conf_text = central_conf.read_text()
    assert 'server_name www.example.test;' in central_conf_text
    assert f'include {sandbox_conf_dir}/*;' in central_conf_text

def test_second_init(fake_home_dir):
    # fill the .exunoplura dir with a mock config
    config_dir = fake_home_dir / '.exunoplura'
    sandbox_conf_dir = config_dir / 'sandbox_configs'
    central_conf = config_dir / 'exunoplura.conf'
    sandbox1_conf = sandbox_conf_dir / 'sandbox1.conf'
    sandbox2_conf = sandbox_conf_dir / 'sandbox2.conf'
    
    central_conf_text = 'server { some random; config entries; }'
    sandbox1_conf_text = 'location { more random; config entries; }'
    sandbox2_conf_text = 'location { even more; meaningless garble; }'
    
    config_dir.mkdir()
    sandbox_conf_dir.mkdir()
    central_conf.write_text(central_conf_text)
    sandbox1_conf.write_text(sandbox1_conf_text)
    sandbox2_conf.write_text(sandbox2_conf_text)

    test_first_init(fake_home_dir)
    
    # assert that the central config was overwritten
    assert central_conf.read_text() != central_conf_text
    # assert that sandbox configs were not overwritten
    assert sandbox1_conf.read_text() == sandbox1_conf_text
    assert sandbox2_conf.read_text() == sandbox2_conf_text

def test_list(fake_home_dir):
    (fake_home_dir / '.exunoplura' / 'sandbox_configs').mkdir(parents=True)
    runner = CliRunner()
    result = runner.invoke(cli, 'list')
    assert result.exit_code == 0
    assert '0 sandboxes' in result.output
