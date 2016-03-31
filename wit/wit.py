import requests
import os

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')

class WitError(Exception):
    pass

def req(access_token, meth, path, params):
    rsp = requests.request(
        meth,
        WIT_API_HOST + path,
        headers={
            'authorization': 'Bearer ' + access_token,
            'accept': 'application/vnd.wit.20160330+json'
        },
        params=params,
    )
    return rsp.json()

def message(access_token, msg):
    params = {}
    if msg:
        params['q'] = msg
    return req(access_token, 'GET', '/message', params)
