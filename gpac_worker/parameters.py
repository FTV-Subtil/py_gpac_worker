
import os
import requests

def get_config_parameter(config, key, param):
    if key in os.environ:
        return os.environ.get(key)

    if param in config:
        return config[param]
    raise RuntimeError("Missing '" + param + "' configuration value.")

def get_parameter(parameters, key):
    for parameter in parameters:
        if parameter['id'] == key:
            value = None
            if 'default' in parameter:
                value = parameter['default']

            if 'value' in parameter:
                value = parameter['value']

            if(parameter['type'] != 'credential'):
                return value

            hostname = get_config_parameter(config['backend'], 'BACKEND_HOSTNAME', 'hostname')
            username = get_config_parameter(config['backend'], 'BACKEND_USERNAME', 'username')
            password = get_config_parameter(config['backend'], 'BACKEND_PASSWORD', 'password')

            response = requests.post(hostname + '/sessions', json={'session': {'email': username, 'password': password}})
            if response.status_code != 200:
                raise("unable to get token to retrieve credential value")

            body = response.json()
            if not 'access_token' in body:
                raise("missing access token in response to get credential value")

            headers = {'Authorization': body['access_token']}
            response = requests.get(hostname + '/credentials/' + value, headers=headers)

            if response.status_code != 200:
                raise("unable to access to credential named: " + key)

            body = response.json()
            return body['data']['value']
    return None
