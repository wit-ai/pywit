import requests
import os

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')
DEFAULT_MAX_STEPS = 5


class WitError(Exception):
    pass


def req(access_token, meth, path, params, payload=None):
    rsp = requests.request(
        meth,
        WIT_API_HOST + path,
        headers={
            'authorization': 'Bearer ' + access_token,
            'accept': 'application/vnd.wit.20160330+json'
        },
        params=params,
        json=payload,
    )
    return rsp.json()


def validate_actions(actions):
    learn_more = 'Learn more at https://wit.ai/docs/quickstart'
    if not isinstance(actions, dict):
        raise WitError('The second parameter should be a dictionary.')
    for action in ['say', 'merge', 'error']:
        if action not in actions:
            raise WitError('The \'' + action + '\' action is missing. ' + learn_more)
    for action in actions.keys():
        if not hasattr(actions[action], '__call__'):
            raise TypeError('The \'' + action + '\' action should be a function.')
    return actions


class Wit:
    access_token = None
    actions = {}

    def __init__(self, access_token, actions):
        self.access_token = access_token
        self.actions = validate_actions(actions)

    def message(self, msg):
        params = {}
        if msg:
            params['q'] = msg
        return req(self.access_token, 'GET', '/message', params)

    def converse(self, session_id, message, context={}):
        params = {'session_id': session_id}
        if message:
            params['q'] = message
        return req(self.access_token, 'POST', '/converse', params, context)

    def run_actions(self, session_id, message, context={},
                    max_steps=DEFAULT_MAX_STEPS):
        if max_steps <= 0:
            raise WitError('max iterations reached')
        rst = self.converse(session_id, message, context)
        if 'type' not in rst:
            raise WitError('couldn\'t find type in Wit response')
        if rst['type'] == 'stop':
            return context
        if rst['type'] == 'msg':
            if 'say' not in self.actions:
                raise WitError('unknown action: say')
            print('Executing say with: {}'.format(rst['msg']))
            self.actions['say'](session_id, rst['msg'])
        elif rst['type'] == 'merge':
            if 'merge' not in self.actions:
                raise WitError('unknown action: merge')
            print('Executing merge')
            context = self.actions['merge'](context, rst['entities'])
            if context is None:
                print('WARN missing context - did you forget to return it?')
                context = {}
        elif rst['type'] == 'action':
            if rst['action'] not in self.actions:
                raise WitError('unknown action: ' + rst['action'])
            print('Executing action {}'.format(rst['action']))
            context = self.actions[rst['action']](context)
            if context is None:
                print('WARN missing context - did you forget to return it?')
                context = {}
        elif rst['type'] == 'error':
            if 'error' not in self.actions:
                raise WitError('unknown action: error')
            print('Executing error')
            self.actions['error'](session_id, message)
        else:
            raise WitError('unknown type: ' + rst['type'])
        return self.run_actions(session_id, None, context, max_steps - 1)
