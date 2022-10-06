import click
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader
#TODO: convert to a package and use PackageLoader
env = Environment(loader=FileSystemLoader('./templates'))
import docker

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

@cli.command()
@click.option('--name', type=click.STRING)
@click.option('--ssh_port', type=click.INT)
@click.option('--http_port', type=click.INT)
def create(name, ssh_port, http_port):
    docker_client = docker.from_env()
    docker_client.containers.run('linuxserver/openssh-server',
            detach=True,
            restart_policy={'Name':'always'},
            ports={2222:ssh_port, 80:http_port},
            environment={
                'USER_NAME':'user', 'USER_PASSWORD':'memes',
                'PASSWORD_ACCESS':'true', 'SUDO_ACCESS':'true'
                }
            )


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
