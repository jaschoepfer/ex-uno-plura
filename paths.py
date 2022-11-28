from pathlib import Path
import urllib


def config_dir():
    return Path.home() / '.exunoplura'

def servers_dir():
    return config_dir() / 'servers'

def server_dir(server_name):
    return servers_dir() / server_name

def server_conf(server_name):
    return servers_dir() / (server_name + '.conf')

def dir_conf(server, path):
    return server_dir(server) / quote(path)

def quote(path):
    return urllib.parse.quote(path, safe='')

