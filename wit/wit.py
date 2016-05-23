import requests
import os
import uuid
import sys
import logging

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')
WIT_API_VERSION = os.getenv('WIT_API_VERSION', '20160516')
DEFAULT_MAX_STEPS = 5
INTERACTIVE_PROMPT = '> '

class WitError(Exception):
    pass

def req(access_token, meth, path, params, **kwargs):
    rsp = requests.request(
        meth,
        WIT_API_HOST + path,
        headers={
            'authorization': 'Bearer ' + access_token,
            'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json'
        },
        params=params,
        **kwargs
    )
    if rsp.status_code > 200:
        raise WitError('Wit responded with status: ' + str(rsp.status_code) +
                       ' (' + rsp.reason + ')')
    json = rsp.json()
    if 'error' in json:
        raise WitError('Wit responded with an error: ' + json['error'])
    return json

def validate_actions(logger, actions):
    learn_more = 'Learn more at https://wit.ai/docs/quickstart'
    if not isinstance(actions, dict):
        logger.warn('The second parameter should be a dictionary.')
    for action in ['say', 'merge', 'error']:
        if action not in actions:
            logger.warn('The \'' + action + '\' action is missing. ' +
                            learn_more)
    for action in actions.keys():
        if not hasattr(actions[action], '__call__'):
            logger.warn('The \'' + action +
                            '\' action should be a function.')
    return actions

class Wit:
    access_token = None
    actions = {}

    def __init__(self, access_token, actions, logger=None):
        self.access_token = access_token
        self.logger = logger or logging.getLogger(__name__)
        self.actions = validate_actions(self.logger, actions)

    def message(self, msg):
        self.logger.debug("Message request: msg=%r", msg)
        params = {}
        if msg:
            params['q'] = msg
        resp = req(self.access_token, 'GET', '/message', params)
        self.logger.debug("Message response: %s", resp)
        return resp


    def converse(self, session_id, message, context=None):
        self.logger.debug("Converse request: session_id=%s msg=%r context=%s",
                          session_id, message, context)
        if context is None:
            context = {}
        params = {'session_id': session_id}
        if message:
            params['q'] = message
        resp = req(self.access_token, 'POST', '/converse', params, json=context)
        self.logger.debug("Message response: %s", resp)
        return resp

    def __run_actions(self, session_id, message, context, max_steps,
                      user_message):
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
            self.logger.info('Executing say with: {}'.format(rst['msg'].encode('utf8')))
            self.actions['say'](session_id, dict(context), rst['msg'])
        elif rst['type'] == 'merge':
            if 'merge' not in self.actions:
                raise WitError('unknown action: merge')
            self.logger.info('Executing merge')
            context = self.actions['merge'](session_id, dict(context),
                                            rst['entities'], user_message)
            if context is None:
                self.logger.warn('missing context - did you forget to return it?')
                context = {}
        elif rst['type'] == 'action':
            if rst['action'] not in self.actions:
                raise WitError('unknown action: ' + rst['action'])
            self.logger.info('Executing action {}'.format(rst['action']))
            context = self.actions[rst['action']](session_id, dict(context))
            if context is None:
                self.logger.warn('missing context - did you forget to return it?')
                context = {}
        elif rst['type'] == 'error':
            if 'error' not in self.actions:
                raise WitError('unknown action: error')
            self.logger.info('Executing error')
            self.actions['error'](session_id, dict(context),
                                  WitError('Oops, I don\'t know what to do.'))
        else:
            raise WitError('unknown type: ' + rst['type'])
        return self.__run_actions(session_id, None, context, max_steps - 1,
                                  user_message)

    def run_actions(self, session_id, message, context=None,
                    max_steps=DEFAULT_MAX_STEPS):
        if context is None:
            context = {}
        return self.__run_actions(session_id, message, context, max_steps,
                                  message)

    def interactive(self, context=None, max_steps=DEFAULT_MAX_STEPS):
        """Runs interactive command line chat between user and bot. Runs
        indefinately until EOF is entered to the prompt.

        context -- optional initial context. Set to {} if omitted
        max_steps -- max number of steps for run_actions.
        """
        if max_steps <= 0:
            raise WitError('max iterations reached')
        # initialize/validate initial context
        context = {} if context is None else context
        # generate type 1 uuid for the session id
        session_id = uuid.uuid1()
        # input/raw_input are not interchangible between python 2 and 3.
        try:
            input_function = raw_input
        except NameError:
            input_function = input
        # main interactive loop. prompt user, pass msg to run_actions, repeat
        while True:
            try:
                message = input_function(INTERACTIVE_PROMPT).rstrip()
            except (KeyboardInterrupt, EOFError):
                return
            context = self.run_actions(session_id, message, context, max_steps)
