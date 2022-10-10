import click
from pathlib import Path
import json
import string
from jinja2 import Environment, FileSystemLoader
#TODO: convert to a package and use PackageLoader
env = Environment(loader=FileSystemLoader('./templates'))
import secrets
import subprocess

@click.group()
def cli():
    pass

@cli.command()
@click.option('--server_name', type=click.STRING, default='_')
def init(server_name):
    # TODO: check if docker & nginx is installed

    config_dir().mkdir(exist_ok=True)
    sandbox_conf_dir().mkdir(exist_ok=True)

    t = env.get_template('exunoplura.conf')
    central_conf_text = t.render(
            server_name=server_name,
            sandbox_dir=str(sandbox_conf_dir())
        )
    central_conf().write_text(central_conf_text)

    state = {'sandboxes':[]}
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
@click.argument('image', type=click.STRING)
@click.argument('args', nargs=-1)
def create(http_port, name, image, args):
    container_name = f'exunoplura_{name}'
    password = gen_password() 
    ssh_port=6001

    try:
        docker_cmd = [
                'docker', 'run', '--detach', f'--name={container_name}', '--restart=always',
                f'--publish={http_port}:80', f'--publish={ssh_port}:2222',
                '--env=USER_NAME=user', f'--env=USER_PASSWORD={password}',
                '--env=SUDO_ACCESS=true', '--env=PASSWORD_ACCESS=true',
                'linuxserver/openssh-server'
            ]
        print(' '.join(docker_cmd))
        subprocess.run(docker_cmd)
    except Exception as e:
        click.echo('Could not start container:' + str(e))
        return

    click.echo(f'Container {container_name} started!')
    click.echo(f'User password (will not be shown again):{password}')

@cli.command()
def remove():
    pass

@cli.command()
def list():
    configs = [x for x in sandbox_conf_dir().iterdir() if x.is_file()]
    click.echo(f'{len(configs)} sandboxes running:')

@cli.command()
def pwgen():
    click.echo(gen_password())    

## Known Paths

def config_dir():
    return Path.home() / '.exunoplura'

def sandbox_conf_dir():
    return config_dir() / 'sandbox_nginx_configs'

def central_conf():
    return config_dir() / 'exunoplura_nginx.conf'

def state_file():
    return config_dir() / 'state.json'


## Utility Functions

def gen_password():
    with open('/usr/share/dict/words') as f:
        words = [word.strip() for word in f if "'" not in word]
    password = ' '.join(secrets.choice(words) for i in range(4))
    return password

if __name__ == '__main__':
    cli()
