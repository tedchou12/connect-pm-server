import requests
import json
import urllib.parse
import base64
from .config import config

def jwt_decode(id_token='') :
    parts = id_token.split('.')
    # header = base64.decodebytes(parts[0])
    payload = parts[1]
    # signature = base64.decodebytes(parts[2])
    payload += '=' * ((4 - len(payload) % 4) % 4)
    payload = base64.b64decode(payload)

    return payload

class google :
    def __init__(self) :
        self.obj_config = config()
        self.client_id = self.obj_config.params['google_client_id']
        self.client_secret = self.obj_config.params['google_client_secret']
        self.auth_endpoint = self.obj_config.params['google_auth_endpoint']
        self.token_endpoint = self.obj_config.params['google_token_endpoint']
        self.response_type = 'code'
        self.grant_type = 'authorization_code'
        self.redirect_uri = self.obj_config.params['hostname'] + 'callback'
        self.state = 'google'
        self.scope = 'openid+email'

    def auth_url(self) :
        params = {'client_id': self.client_id,
                  'redirect_uri': urllib.parse.quote(self.redirect_uri),
                  'response_type': self.response_type,
                  'scope': self.scope,
                  'state': self.state}

        query_strings = []
        for param in params :
            query_strings.append(param + '=' + params[param])

        return self.auth_endpoint + '?' + '&'.join(query_strings)

    def get_token(self, code='') :
        headers = {'content-type': 'application/json'}
        params = {'code': code,
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'redirect_uri': self.redirect_uri,
                  'grant_type': self.grant_type}
        response = requests.post(self.token_endpoint, data=json.dumps(params), headers=headers)
        data = json.loads(response.text)

        if 'id_token' in data :
            return json.loads(jwt_decode(data['id_token']))

        return False

class microsoft :
    def __init__(self) :
        self.obj_config = config()
        self.client_id = self.obj_config.params['microsoft_client_id']
        self.client_secret = self.obj_config.params['microsoft_client_secret']
        self.auth_endpoint = self.obj_config.params['microsoft_auth_endpoint']
        self.token_endpoint = self.obj_config.params['microsoft_token_endpoint']
        self.response_type = 'code'
        self.grant_type = 'authorization_code'
        self.redirect_uri = self.obj_config.params['hostname'] + 'callback'
        self.state = 'microsoft'
        self.scope = 'openid+email'

    def auth_url(self) :
        params = {'client_id': self.client_id,
                  'redirect_uri': urllib.parse.quote(self.redirect_uri),
                  'response_type': self.response_type,
                  'scope': self.scope,
                  'state': self.state}

        query_strings = []
        for param in params :
            query_strings.append(param + '=' + params[param])

        return self.auth_endpoint + '?' + '&'.join(query_strings)

    def get_token(self, code='') :
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params = {'code': code,
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'redirect_uri': self.redirect_uri,
                  'grant_type': self.grant_type}
        response = requests.post(self.token_endpoint, data=params, headers=headers)
        data = json.loads(response.text)

        if 'id_token' in data :
            return json.loads(jwt_decode(data['id_token']))

        return False

class hac :
    def __init__(self) :
        self.obj_config = config()
        self.client_id = self.obj_config.params['hac_client_id']
        self.client_secret = self.obj_config.params['hac_client_secret']
        self.auth_endpoint = self.obj_config.params['hac_auth_endpoint']
        self.token_endpoint = self.obj_config.params['hac_token_endpoint']
        self.response_type = 'code'
        self.grant_type = 'authorization_code'
        self.redirect_uri = self.obj_config.params['hostname'] + 'callback'
        self.state = 'hac'
        self.scope = 'openid+email'

    def auth_url(self) :
        params = {'client_id': self.client_id,
                  'redirect_uri': urllib.parse.quote(self.redirect_uri),
                  'response_type': self.response_type,
                  'scope': self.scope,
                  'state': self.state}

        query_strings = []
        for param in params :
            query_strings.append(param + '=' + params[param])

        return self.auth_endpoint + '?' + '&'.join(query_strings)

    def get_token(self, code='') :
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params = {'code': code,
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'redirect_uri': self.redirect_uri,
                  'grant_type': self.grant_type}
        response = requests.post(self.token_endpoint, data=params, headers=headers)
        data = json.loads(response.text)

        if 'id_token' in data :
            return json.loads(jwt_decode(data['id_token']))

        return False
