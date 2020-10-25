import requests
import os

class Proxy(object):

    def __init__(self, host, user=None, password=None, token=None) -> None:
        self._host = host.rstrip('/')
        self._apikey = None

        if token is not None:
            self._apikey = token
        if user is not None:
            self._apikey = self.post('/api/login', json={'email': user, 'password': password})['token']


    def post(self, route, data=None, json=None, params=None):
        if params is None:
            params = {}
        if self._apikey is not None:
            params['apiKey'] = self._apikey

        if data is not None:
            response = requests.post(self._host + '/api' + route, data=data, params=params)
        elif json is not None:
            response = requests.post(self._host + '/api' + route, json=data, params=params)
        else:
            response = requests.post(self._host + '/api' + route, params=params)

        if response.status_code != 200:
            raise Exception(f'Error({response.status_code}) with message: {response.text} !')

        return response.json()

    def put(self, route, data=None, json=None, params=None, files=None):
        if params is None:
            params = {}
        if self._apikey is not None:
            params['apiKey'] = self._apikey

        if files is not None:
            del_tmp = False
            if 'df' in files:
                del_tmp = True
                files['df'].to_csv('tmp.csv')
                files['file'] = 'tmp.csv'
                del files['df']

            files['file'] = open(files['file'],'rb')
            data = {}
            data['source_type'] = 'file'

            response = requests.put(self._host + '/api' + route, files=files, data=data)

            if del_tmp:
                os.remove('tmp.csv')


        elif data is not None:
            response = requests.put(self._host + '/api' + route, data=data, params=params)
        elif json is not None:
            response = requests.put(self._host + '/api' + route, json=data, params=params)
        else:
            response = requests.put(self._host + '/api' + route, params=params)

        if response.status_code != 200:
            raise Exception(f'Error({response.status_code}) with message: {response.text} !')

        return response.json()

    def get(self, route, params=None):
        if params is None:
            params = {}
        if self._apikey is not None:
            params['apiKey'] = self._apikey

        response = requests.get(self._host + '/api' + route, params=params)
        if response.status_code != 200:
            raise Exception(f'Error({response.status_code}) with message: {response.text} !')
        return response.json()

    def delete(self, route, params=None):
        if params is None:
            params = {}
        if self._apikey is not None:
            params['apiKey'] = self._apikey

        response = requests.delete(self._host + '/api' + route, params=params)

        if response.status_code != 200:
            raise Exception(f'Error({response.status_code}) with message: {response.text} !')

        return response.json()

    def ping(self):
        try:
            return self.get('/util/ping')['status'] == 'ok'
        except Exception as _:
            return False