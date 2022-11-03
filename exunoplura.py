import click
from pathlib import Path
import json
import string
from jinja2 import Environment, FileSystemLoader
#TODO: convert to a package and use PackageLoader
env = Environment(loader=FileSystemLoader('./templates'))

@click.group()
def cli():
    pass

@cli.command()
@click.option('--server_name', type=click.STRING, default='_')
def init(server_name):
    # TODO: check if nginx is installed

    config_dir().mkdir(exist_ok=True)
    location_conf_dir().mkdir(exist_ok=True)

    t = env.get_template('exunoplura.conf')
    central_conf_text = t.render(
            server_name=server_name,
            location_dir=str(location_conf_dir())
        )
    central_conf().write_text(central_conf_text)

    state = {'locations':[]}
    state_file().write_text(json.dumps(state))

    click.echo(
        'To complete initialization, import exunoplura_nginx.conf into your nginx config.\n'
        'Depending on your nginx installation, that could look like this:\n'
        f'  `sudo ln {central_conf()} /etc/nginx/sites-enabled/`'
    )

def validate_name(ctx, param, name):
    alphanumerics = string.ascii_letters + string.digits
    permitted_chars = alphanumerics + '_-'
    
    name_invalid = any([
        name == '',
        name[0] not in alphanumerics,
        any(char not in permitted_chars for char in name)
    ])

    if name_invalid:
        raise click.BadParameter('format must be [a-zA-Z0-9][a-zA-Z0-9_-]*')

    return name

@cli.command()
@click.option('--http_port', type=click.INT)
@click.argument('name', type=click.UNPROCESSED, callback=validate_name)
def create(http_port, name, image, args):
    pass

@cli.command()
def remove():
    pass

@cli.command()
def list():
    configs = [x for x in location_conf_dir().iterdir() if x.is_file()]
    click.echo(f'{len(configs)} locations set up:')

## Known Paths

def config_dir():
    return Path.home() / '.exunoplura'

def location_conf_dir():
    return config_dir() / 'location_configs'

def central_conf():
    return config_dir() / 'exunoplura_nginx.conf'

def state_file():
    return config_dir() / 'state.json'


## Utility Functions
if __name__ == '__main__':
    cli()
