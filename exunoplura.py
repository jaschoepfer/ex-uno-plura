# builtins
import string
import os
from operator import xor
# 3rd party imports
import click
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('exunoplura', 'templates'))
# project imports
import paths


@click.group()
def cli():
    pass

def validate_server_name(ctx, param, name):
    permitted_chars = string.ascii_letters + string.digits + '_-.'
    name_invalid = any(char not in permitted_chars for char in name)
    if name_invalid:
        raise click.BadParameter('server name format is [a-zA-Z0-9_-.]')

    if len(name) == 0:
        return '_'

    return name

@cli.command('create-server')
@click.argument('name', type=click.UNPROCESSED, callback=validate_server_name)
@click.option('--cert', type=click.Path(exists=True, dir_okay=False, readable=False))
@click.option('--key', type=click.Path(exists=True, dir_okay=False, readable=False))
def create_server(name, cert, key):
    if xor(bool(cert), bool(key)):
        raise click.UsageError('Both certificate and key are required to enable SSL!')

    server_dir = paths.server_dir(name)
    server_dir.mkdir(exist_ok=True, parents=True)
    server_conf = paths.server_conf(name)
    t = env.get_template('server.conf')
    server_conf_text = t.render(
            server_name=name,
            ssl_cert=cert,
            ssl_key=key,
            location_dir=str(server_dir)
        )
    server_conf.write_text(server_conf_text)

    click.echo(
        f'To activate your server, import { name }.conf into your nginx config.\n'
        'Depending on your nginx setup, that could look like this:\n'
        f'sudo ln -s { server_conf } /etc/nginx/sites-enabled/'
    )

def validate_server(ctx, param, server):
    validate_server_name(ctx, param, server)
    if not paths.server_conf(server).is_file():
        raise click.ClickException(f'unknown server name "{ server }"')

    paths.server_dir(server).mkdir(exist_ok=True)

    return server

def validate_path(ctx, param, path):
    if not path.startswith('/'):
        return '/' + path

    return path

@cli.command('create-dir')
@click.argument('server', type=click.UNPROCESSED, callback=validate_server)
@click.argument('path', type=click.UNPROCESSED, callback=validate_path)
@click.option('--proxy-port', type=click.INT)
def create_dir(server, path, proxy_port):
    t = env.get_template('dir.conf')
    dir_conf_text = t.render(
            path=path,
            proxy_port=proxy_port
        )
    paths.dir_conf(server, path).write_text(dir_conf_text)

if __name__ == '__main__':
    cli()

