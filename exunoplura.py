import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
#TODO: convert to a package and use PackageLoader
env = Environment(loader=FileSystemLoader('./templates'))


@click.group()
def cli():
    pass

@cli.command()
@click.option('--servername', type=click.STRING, default='_')
def init(servername):
    # TODO: check if docker & nginx is installed

    config_dir().mkdir(exist_ok=True)
    sandbox_conf_dir().mkdir(exist_ok=True)

    t = env.get_template('exunoplura.conf')
    central_conf_text = t.render(
            server_name=servername,
            sandbox_dir=str(sandbox_conf_dir())
        )
    central_conf().write_text(central_conf_text)

    click.echo(
        'To complete initialization, import exunoplura_nginx.conf into your nginx config.\n'
        'Depending on your nginx installation, that could look like this:\n'
        f'  `sudo ln {central_conf()} /etc/nginx/sites-enabled/`'
    )

@cli.command()
def create():
    pass

@cli.command()
def remove():
    pass

@cli.command()
def list():
    configs = [x for x in sandbox_conf_dir().iterdir() if x.is_file()]
    click.echo(f'{len(configs)} sandboxes running:')


# Known Paths Section

def config_dir():
    return Path.home() / '.exunoplura'

def sandbox_conf_dir():
    return config_dir() / 'sandbox_nginx_configs'

def central_conf():
    return config_dir() / 'exunoplura_nginx.conf'

def state_file():
    return config_dir() / 'state.json'


if __name__ == '__main__':
    cli()
