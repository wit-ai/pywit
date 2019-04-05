# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

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
    
    def post_samples(self, text, entities, *args):
        """  Validate samples (sentence + entities annotations) to train your app programmatically.
        Each entity in entities list should be like this:
        
        "entity": "car",
        "value": "blue toyota",
        "start": 9,
        "end": 20,
        "subentities": [
          {
            "entity":"color",
            "value": "blue",
            "start": 0,
            "end": 4
          }]
          
          
        :param text: The text (sentence) you want your app to understand.
        :param entities: The list of entities appearing in this sentence, that you want your app to extract once it is trained. (use the format above)
        
        :return: Dictionary that contains if the samples were sent ['sent'], and number of samples sent ['n']"""
        params = {'v': WIT_API_VERSION}
        data = []
        if text and entities:
            data.append({'text': text,'entities': entities})
        if len(args)>1:
            x=0
            while x<len(args):
                data.append({'text': args[x],'entities': args[x+1]})
                x+=2
        return req(self.logger, self.access_token, 'POST', '/samples', params,data=json.dumps(data))
    
    def get_samples(self, limit, offset=None, entity_ids=None, entity_values=None, negative=None):
        """Return a list of Samples.
        
        :param limit: Max number of samples to return. Must be between 1 and 10000 inclusive.
        :param offset: Number of samples to skip. Must be >= 0. Default is 0.
        :param entity_ids: List of names of the entities that all returned samples must include. 
        :param entity_values: List of values of the specified entities that all returned samples must include. Note entity_values can only be specified if entity_ids is specified.
        :param negative: A flag to show the negative samples of the specified entity_id. 
        
        :return: a list of all samples."""
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if entity_ids:
            params['entity_ids'] = entity_ids
        if entity_values:
            params['entity_values'] = negative
        if negative:
            params['negative'] = negative
        return req(self.logger, self.access_token, 'GET', '/samples', params)
    
    def post_app(self, name, lang, private, desc=None):
        """Creates a new app for an existing user.
        :param name: Name of the new app.
        :param lang: Language code (ISO alpha-2 code) e.g : "en". 
        :param private: Private if “true”
        
        :return: A dictionary with the new app's access token ['access_token'] and the new app's id ['app_id']"""
        params = {'v': WIT_API_VERSION}
        data = None
        if name and lang and private:
            data = {'name': name,'lang': lang,'private': str(private).lower()}
        if desc:
            data['desc'] = desc
        return req(self.logger, self.access_token, 'POST', '/apps', params,data=json.dumps(data))
    
    def get_apps(self, limit, offset=None):
        """Returns an array of all apps that you own.
        NOTE: Does not return shared apps.
        
        :param limit: Max number of apps to return. Must be between 1 and 10000 inclusive (recommended max size is 500).
        :param offset: Number of apps to skip. Must be >= 0. Default is 0.
        
        :return: List of all apps with their information."""
        params = {'v': WIT_API_VERSION}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        return req(self.logger, self.access_token, 'GET', '/apps', params)
    
    def update_app(self, app_id, name=None, lang=None, private=None, timezone=None, desc=None):
        """Updates an app with the given attributes.
        
        :param name: Name of the new app
        :param lang: Language code e.g: "en".
        :param private: Private if true.
        :param timezone: Default timezone of the app. Must be a canonical ID. Example: “America/Los_Angeles”
        :param desc: Short sentence describing your app.
        
        :return: Dictionary with a boolean that represents the success of the operation ['success']."""
        params = {'v': WIT_API_VERSION}
        data = {}
        if name:
            data['name'] = name
        if lang:
            data['lang'] = lang
        if private:
            data['private'] = private
        if timezone:
            data['timezone'] = timezone
        if desc:
            data['desc'] = desc
        return req(self.logger, self.access_token, 'PUT', '/apps/'+app_id, params,data=json.dumps(data))
    
    def get_app(self, app_id):
        """Returns a map representation of the specified app.
        
        :param app_id: The ID of the app you want to information about.
        
        :return: Information about the requested app."""
        return req(self.logger, self.access_token, 'GET', '/apps/'+app_id, {})
    
    def delete_app(self, app_id):
        """Permanently delete the app.
        NOTE: You must be the creator of the app to be able to delete it.
        
        :param app_id: ID of the want-to-be deleted app.
        
        :return: Dictionary with a boolean that represents the success of the operation ['success']."""
        return req(self.logger, self.access_token, 'DELETE', '/apps/'+app_id, {})

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
