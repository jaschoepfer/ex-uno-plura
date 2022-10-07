import click
from pathlib import Path
import json
import string
from jinja2 import Environment, FileSystemLoader
#TODO: convert to a package and use PackageLoader
env = Environment(loader=FileSystemLoader('./templates'))
import docker
import secrets

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
@click.option('--name', type=click.UNPROCESSED, callback=validate_name, prompt=True)
@click.option('--ssh_port', type=click.INT, default=0)
@click.option('--http_port', type=click.INT, default=0)
def create(name, ssh_port, http_port):
    password = gen_password() 

    try:
        docker_client = docker.from_env()
        c = docker_client.containers.run('linuxserver/openssh-server',
                name=f'exunoplura_{name}',
                detach=True,
                restart_policy={'Name': 'always'},
                ports={2222:ssh_port, 80:http_port},
                environment={
                    'USER_NAME':'user', 'USER_PASSWORD':password,
                    'PASSWORD_ACCESS':'true', 'SUDO_ACCESS':'true'
                }
            )
    except Exception as e:
        click.echo('Could not start container:' + str(e))
        return

    click.echo(f'Container {c.name} started!')
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
