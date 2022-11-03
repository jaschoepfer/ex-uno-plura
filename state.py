import json
import paths


def read():
    return json.loads(paths.state_file().read_text())

def write(new_state):
    paths.state_file().write_text(json.dumps(new_state))

def init():
    write({ 'locations': [] })

def get_locations():
    return read()['locations']

def add_location(name, http_port):
    state = read()
    state['locations'].append({
        'name': name,
        'http-port': http_port 
    })
    write(state)

