import string
# 3rd party imports
import click
from jinja2 import Environment, FileSystemLoader
#TODO: convert to a package and use PackageLoader
env = Environment(loader=FileSystemLoader('./templates'))
# local imports
import paths
import state

@click.group()
def cli():
    pass

@cli.command()
@click.option('--server_name', type=click.STRING, default='_')
def init(server_name):
    # TODO: check if nginx is installed

    loc_dir = paths.location_conf_dir()
    loc_dir.mkdir(exist_ok=True, parents=True)

    t = env.get_template('exunoplura.conf')
    central_conf_text = t.render(
            server_name=server_name,
            location_dir=str(loc_dir)
        )
    paths.central_conf().write_text(central_conf_text)

    state.init()

    click.echo(
        'To complete initialization, import exunoplura_nginx.conf into your nginx config.\n'
        'Depending on your nginx installation, that could look like this:\n'
        f'  `sudo ln -s {paths.central_conf()} /etc/nginx/sites-enabled/`'
    )

def validate_name(ctx, param, name):
    alphanumerics = string.ascii_letters + string.digits
    permitted_chars = alphanumerics + '_-'
    
    name_invalid = any((
        name == '',
        name[0] not in alphanumerics,
        any(char not in permitted_chars for char in name)
    ))

    if name_invalid:
        raise click.BadParameter('format must be [a-zA-Z0-9][a-zA-Z0-9_-]*')

    return name

@cli.command()
@click.argument('name', type=click.UNPROCESSED, callback=validate_name)
@click.argument('http_port', type=click.INT)
def create(http_port, name):
    state.add_location(name, http_port)

    loc_conf = paths.location_conf_dir() / f'{ name }.conf'
    t = env.get_template('location.conf')
    loc_conf_text = t.render(
            name=name,
            http_port=http_port
        )
    loc_conf.write_text(loc_conf_text)

@cli.command()
def remove():
    pass

@cli.command()
def list():
    configs = [x for x in paths.location_conf_dir().iterdir() if x.is_file()]
    click.echo(f'{len(configs)} locations set up:')


if __name__ == '__main__':
    cli()

