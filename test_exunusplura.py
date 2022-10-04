import pytest
from click.testing import CliRunner
from exunusplura import cli
from pathlib import Path


@pytest.fixture(autouse=True)
def fake_home_dir(monkeypatch, tmp_path):
    def fake_home():
        return tmp_path
    monkeypatch.setattr('pathlib.Path.home', fake_home)
    yield tmp_path


def test_first_init(fake_home_dir):
    pass

def test_second_init():
    pass

def test_list(fake_home_dir):
    (fake_home_dir / '.exunusplura' / 'sandbox_configs').mkdir(parents=True)
    runner = CliRunner()
    result = runner.invoke(cli, 'list')
    assert result.exit_code == 0
    assert '0 sandboxes' in result.output
