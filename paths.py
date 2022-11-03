from pathlib import Path


def config_dir():
    return Path.home() / '.exunoplura'

def location_conf_dir():
    return config_dir() / 'location_configs'

def central_conf():
    return config_dir() / 'exunoplura_nginx.conf'

def state_file():
    return config_dir() / 'state.json'

