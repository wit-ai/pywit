from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import os
import requests
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')
WIT_API_VERSION = os.getenv('WIT_API_VERSION', '20160516')
DEFAULT_MAX_STEPS = 5
INTERACTIVE_PROMPT = '> '
LEARN_MORE = 'Learn more at https://wit.ai/docs/quickstart'


class WitError(Exception):
    pass


def req(logger, access_token, meth, path, params, **kwargs):
    full_url = WIT_API_HOST + path
    logger.debug('%s %s %s', meth, full_url, params)
    headers = {
        'authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json'
    }
    headers.update(kwargs.pop('headers', {}))
    rsp = requests.request(
        meth,
        full_url,
        headers=headers,
        params=params,
        **kwargs
    )
    if rsp.status_code > 200:
        raise WitError('Wit responded with status: ' + str(rsp.status_code) +
                       ' (' + rsp.reason + ')')
    json = rsp.json()
    if 'error' in json:
        raise WitError('Wit responded with an error: ' + json['error'])

    logger.debug('%s %s %s', meth, full_url, json)
    return json


class Wit(object):
    access_token = None
    _sessions = {}

    def __init__(self, access_token, logger=None):
        self.access_token = access_token
        self.logger = logger or logging.getLogger(__name__)

    def message(self, msg, context=None, n=None, verbose=None):
        params = {}
        if verbose:
            params['verbose'] = verbose
        if n is not None:
            params['n'] = n
        if msg:
            params['q'] = msg
        if context:
            params['context'] = json.dumps(context)
        resp = req(self.logger, self.access_token, 'GET', '/message', params)
        return resp

    def speech(self, audio_file, verbose=None, headers=None):
        """ Sends an audio file to the /speech API.
        Uses the streaming feature of requests (see `req`), so opening the file
        in binary mode is strongly reccomended (see
        http://docs.python-requests.org/en/master/user/advanced/#streaming-uploads).
        Add Content-Type header as specified here: https://wit.ai/docs/http/20160526#post--speech-link

        :param audio_file: an open handler to an audio file
        :param verbose:
        :param headers: an optional dictionary with request headers
        :return:
        """
        params = {}
        headers = headers or {}
        if verbose:
            params['verbose'] = True
        resp = req(self.logger, self.access_token, 'POST', '/speech', params,
                   data=audio_file, headers=headers)
        return resp

    def interactive(self, handle_message=None, context=None):
        """Runs interactive command line chat between user and bot. Runs
        indefinitely until EOF is entered to the prompt.

        handle_message -- optional function to customize your response.
        context -- optional initial context. Set to {} if omitted
        """
        if context is None:
            context = {}

        history = InMemoryHistory()
        while True:
            try:
                message = prompt(INTERACTIVE_PROMPT, history=history, mouse_support=True).rstrip()
            except (KeyboardInterrupt, EOFError):
                return
            if handle_message is None:
                print(self.message(message, context))
            else:
                print(handle_message(self.message(message, context)))
