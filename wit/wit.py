# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

# pyre-strict

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import os
from urllib.parse import quote

import requests
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

# pyre-fixme[5]: Global expression must be annotated.
WIT_API_HOST = os.getenv("WIT_URL", "https://api.wit.ai")
# pyre-fixme[5]: Global expression must be annotated.
WIT_API_VERSION = os.getenv("WIT_API_VERSION", "20200513")
INTERACTIVE_PROMPT = "> "
LEARN_MORE = "Learn more at https://wit.ai/docs/quickstart"


class WitError(Exception):
    pass


# pyre-fixme[3]: Return type must be annotated.
# pyre-fixme[2]: Parameter must be annotated.
def req(logger, access_token, meth, path, params, **kwargs):
    full_url = WIT_API_HOST + path
    logger.debug("%s %s %s", meth, full_url, params)
    headers = {
        "authorization": "Bearer " + access_token,
        "accept": "application/vnd.wit." + WIT_API_VERSION + "+json",
    }
    headers.update(kwargs.pop("headers", {}))
    rsp = requests.request(meth, full_url, headers=headers, params=params, **kwargs)
    if rsp.status_code > 200:
        raise WitError(
            "Wit responded with status: "
            + str(rsp.status_code)
            + " ("
            + rsp.reason
            + ")"
        )
    json = rsp.json()
    if "error" in json:
        raise WitError("Wit responded with an error: " + json["error"])

    logger.debug("%s %s %s", meth, full_url, json)
    return json


class Wit:
    """
    Main client class for interacting with the Wit.ai API.
    Provides comprehensive functionality for natural language processing,
    intent detection, entity management, and conversational AI capabilities.
    """

    # pyre-fixme[4]: Attribute must be annotated.
    access_token = None
    # pyre-fixme[4]: Attribute must be annotated.
    _sessions = {}

    # pyre-fixme[2]: Parameter must be annotated.
    def __init__(self, access_token, logger=None) -> None:
        self.access_token = access_token
        # pyre-fixme[4]: Attribute must be annotated.
        self.logger = logger or logging.getLogger(__name__)

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def message(self, msg, context=None, n=None, verbose=None):
        params = {}
        if n is not None:
            params["n"] = n
        if msg:
            params["q"] = msg
        if context:
            params["context"] = json.dumps(context)
        if verbose:
            params["verbose"] = verbose
        resp = req(self.logger, self.access_token, "GET", "/message", params)
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def speech(self, audio_file, headers=None, verbose=None):
        """Sends an audio file to the /speech API.
        Uses the streaming feature of requests (see `req`), so opening the file
        in binary mode is strongly recommended (see
        http://docs.python-requests.org/en/master/user/advanced/#streaming-uploads).
        Add Content-Type header as specified here: https://wit.ai/docs/http/20200513#post--speech-link

        :param audio_file: an open handler to an audio file
        :param headers: an optional dictionary with request headers
        :param verbose: for legacy versions, get extra information
        :return:
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            "/speech",
            params,
            data=audio_file,
            headers=headers,
        )
        return resp

    # pyre-fixme[2]: Parameter must be annotated.
    def interactive(self, handle_message=None, context=None) -> None:
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
                message = prompt(
                    INTERACTIVE_PROMPT, history=history, mouse_support=True
                ).rstrip()
            except (KeyboardInterrupt, EOFError):
                return
            if handle_message is None:
                print(self.message(message, context))
            else:
                print(handle_message(self.message(message, context)))

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def intent_list(self, headers=None, verbose=None):
        """
        Returns names of all intents associated with your app.
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        resp = req(
            self.logger, self.access_token, "GET", "/intents", params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def detect_language(self, msg, n=None, headers=None, verbose=None):
        """
        Returns the list of the top detected locales for the text message.
        """
        params = {}
        headers = headers or {}
        if msg:
            params["q"] = msg
        if verbose:
            params["verbose"] = True
        if n is not None:
            params["n"] = n
        resp = req(
            self.logger, self.access_token, "GET", "/language", params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def intent_info(self, intent_name, headers=None, verbose=None):
        """
        Returns all available information about an intent.

        :param intent_name: name of existing intent
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/intents/" + quote(intent_name, safe="")
        resp = req(
            self.logger, self.access_token, "GET", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def entity_list(self, headers=None, verbose=None):
        """
        Returns list of all entities associated with your app.
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        resp = req(
            self.logger, self.access_token, "GET", "/entities", params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def entity_info(self, entity_name, headers=None, verbose=None):
        """
        Returns all available information about an entity.

        :param entity_name: name of existing entity
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/entities/" + quote(entity_name, safe="")
        resp = req(
            self.logger, self.access_token, "GET", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def trait_list(self, headers=None, verbose=None):
        """
        Returns list of all traits associated with your app.
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        resp = req(
            self.logger, self.access_token, "GET", "/traits", params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def trait_info(self, trait_name, headers=None, verbose=None):
        """
        Returns all available information about a trait.

        :param trait_name: name of existing trait
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/traits/" + quote(trait_name, safe="")
        resp = req(
            self.logger, self.access_token, "GET", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_intent(self, intent_name, headers=None, verbose=None):
        """
        Delete an intent associated with your app.

        :param intent_name: name of intent to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/intents/" + quote(intent_name, safe="")
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_entity(self, entity_name, headers=None, verbose=None):
        """
        Delete an entity associated with your app.

        :param entity_name: name of entity to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/entities/" + quote(entity_name, safe="")
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_role(self, entity_name, role_name, headers=None, verbose=None):
        """
        Deletes a role associated with the entity.

                :param entity_name: name of entity whose particular role is to be deleted
        :param role_name: name of role to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = (
            "/entities/" + quote(entity_name, safe="") + ":" + quote(role_name, safe="")
        )
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_keyword(self, entity_name, keyword_name, headers=None, verbose=None):
        """
        Deletes a keyword associated with the entity.

                :param entity_name: name of entity whose particular keyword is to be deleted
        :param keyword_name: name of keyword to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = (
            "/entities/"
            + quote(entity_name, safe="")
            + "/keywords/"
            + quote(keyword_name, safe="")
        )
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def delete_synonym(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        entity_name,
        # pyre-fixme[2]: Parameter must be annotated.
        keyword_name,
        # pyre-fixme[2]: Parameter must be annotated.
        synonym_name,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Delete a synonym of the keyword of the entity.

                :param entity_name: name of entity whose particular keyword is to be deleted
        :param keyword_name: name of keyword to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = (
            "/entities/"
            + quote(entity_name, safe="")
            + "/keywords/"
            + quote(keyword_name, safe="")
            + "/synonyms/"
            + quote(synonym_name, safe="")
        )
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_trait(self, trait_name, headers=None, verbose=None):
        """
        Delete a trait associated with your app.

        :param intent_name: name of intent to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/traits/" + quote(trait_name, safe="")
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_trait_value(self, trait_name, value_name, headers=None, verbose=None):
        """
        Deletes a value associated with the trait.

                :param trait_name: name of trait whose particular value is to be deleted
        :param value_name: name of value to be deleted
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = (
            "/traits/"
            + quote(trait_name, safe="")
            + "/values/"
            + quote(value_name, safe="")
        )
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def get_utterances(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        limit,
        # pyre-fixme[2]: Parameter must be annotated.
        offset=None,
        # pyre-fixme[2]: Parameter must be annotated.
        intents=None,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Returns a JSON array of utterances.

                :param limit: number of utterances to return
        :param offset: number of utterances to skip
        :param intents: list of intents to filter the utterances
        """
        params = {}
        headers = headers or {}
        if limit is not None:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if intents:
            params["intents"] = intents
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "GET",
            "/utterances",
            params,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_utterances(self, utterances, headers=None, verbose=None):
        """
        Delete utterances from your app.

                :param utterances: list of utterances to be deleted
        """
        params = {}
        headers = headers or {}
        data = []
        for utterance in utterances:
            data.append({"text": utterance})
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "DELETE",
            "/utterances",
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def get_apps(self, limit, offset=None, headers=None, verbose=None):
        """
        Returns an array of all your apps.

                :param limit: number of apps to return
        :param offset: number of utterances to skip
        """
        params = {}
        headers = headers or {}
        if limit is not None:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger, self.access_token, "GET", "/apps", params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def app_info(self, app_id, headers=None, verbose=None):
        """
        Returns an object representation of the specified app.

        :param app_id: ID of existing app
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/apps/" + quote(app_id, safe="")
        resp = req(
            self.logger, self.access_token, "GET", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_app(self, app_id, headers=None, verbose=None):
        """
        Returns an object representation of the specified app.

        :param app_id: ID of existing app
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/apps/" + quote(app_id, safe="")
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def app_versions(self, app_id, headers=None, verbose=None):
        """
        Returns an array of all tag groups for an app.

        :param app_id: ID of existing app
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/apps/" + quote(app_id, safe="") + "/tags"
        resp = req(
            self.logger, self.access_token, "GET", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def app_version_info(self, app_id, tag_id, headers=None, verbose=None):
        """
        Returns an object representation of the specified app.

        :param app_id: ID of existing app
        :param tag_id: name of tag
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        endpoint = "/apps/" + quote(app_id, safe="") + "/tags/" + quote(tag_id, safe="")
        resp = req(
            self.logger, self.access_token, "GET", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def create_app_version(self, app_id, tag_name, headers=None, verbose=None):
        """
        Create a new version of your app.

                :param app_id: ID of existing app
                :param tag_name: name of tag
        """
        params = {}
        headers = headers or {}
        data = {"tag": tag_name}
        endpoint = "/apps/" + app_id + "/tags/"
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def delete_app_version(self, app_id, tag_name, headers=None, verbose=None):
        """
        Delete a specific version of your app.

                :param app_id: ID of existing app
                :param tag_name: name of tag
        """
        params = {}
        headers = headers or {}
        endpoint = (
            "/apps/" + quote(app_id, safe="") + "/tags/" + quote(tag_name, safe="")
        )
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger, self.access_token, "DELETE", endpoint, params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def export(self, headers=None, verbose=None):
        """
        Get a URL where you can download a ZIP file containing all of your app data.
        """
        params = {}
        headers = headers or {}
        if verbose:
            params["verbose"] = True
        resp = req(
            self.logger, self.access_token, "GET", "/export", params, headers=headers
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def import_app(self, name, private, zip_file, headers=None, verbose=None):
        """
        Create a new app with all the app data from the exported app.

                :param name: name of the new app
        :param private: private if true
        """
        params = {}
        headers = headers or {}
        if name is not None:
            params["name"] = name
        if private:
            params["private"] = private
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            "/import",
            params,
            data=zip_file,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def create_intent(self, intent_name, headers=None, verbose=None):
        """
        Creates a new intent with the given attributes.

                :param intent_name: name of intent to be created
        """
        params = {}
        headers = headers or {}
        data = {"name": intent_name}
        endpoint = "/intents"
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def create_entity(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        entity_name,
        # pyre-fixme[2]: Parameter must be annotated.
        roles,
        # pyre-fixme[2]: Parameter must be annotated.
        lookups=None,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Creates a new intent with the given attributes.

                :param entity_name: name of entity to be created
                :param roles: list of roles you want to create for the entity
                :param lookups:  list of lookup strategies
        """
        params = {}
        headers = headers or {}
        data = {"name": entity_name, "roles": roles}
        endpoint = "/entities"
        if lookups:
            data["lookups"] = lookups
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def update_entity(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        current_entity_name,
        # pyre-fixme[2]: Parameter must be annotated.
        new_entity_name,
        # pyre-fixme[2]: Parameter must be annotated.
        roles,
        # pyre-fixme[2]: Parameter must be annotated.
        lookups=None,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Updates the attributes of an entity.

                :param entity_name: name of entity to be updated
                :param roles: updated list of roles
                :param lookups:  updated list of lookup strategies
        """
        params = {}
        headers = headers or {}
        data = {"name": new_entity_name, "roles": roles}
        endpoint = "/entities/" + quote(current_entity_name, safe="")
        if lookups:
            data["lookups"] = lookups
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "PUT",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def add_keyword_value(self, entity_name, data, headers=None, verbose=None):
        """
        Add a possible value into the list of keywords for the keywords entity.

                :param entity_name: name of entity to which keyword is to be added
        """
        params = {}
        headers = headers or {}
        endpoint = "/entities/" + quote(entity_name, safe="") + "/keywords"
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def create_synonym(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        entity_name,
        # pyre-fixme[2]: Parameter must be annotated.
        keyword_name,
        # pyre-fixme[2]: Parameter must be annotated.
        synonym,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Create a new synonym of the canonical value of the keywords entity.

                :param entity_name: name of entity to which synonym is to be added
                :param keyword_name: name of keyword to which synonym is to be added
                :param synonym: name of synonym to be created
        """
        params = {}
        headers = headers or {}
        endpoint = (
            "/entities/"
            + quote(entity_name, safe="")
            + "/keywords/"
            + quote(keyword_name, safe="")
            + "/synonyms"
        )
        data = {"synonym": synonym}
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def create_trait(self, trait_name, values, headers=None, verbose=None):
        """
        Creates a new trait with the given attributes.

                :param trait_name: name of trait to be created
                :param values: list of values for the trait
        """
        params = {}
        headers = headers or {}
        data = {"name": trait_name, "values": values}
        endpoint = "/traits"
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def create_trait_value(self, trait_name, new_value, headers=None, verbose=None):
        """
        Creates a new trait with the given attributes.

                :param trait_name: name of trait to which new value is to be added
                :param new_value: name of new trait value
        """
        params = {}
        headers = headers or {}
        data = {"value": new_value}
        endpoint = "/traits/" + quote(trait_name, safe="") + "/values"
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def train(self, data, headers=None, verbose=None):
        """
        Train your utterances.

                :param data: array of utterances with required arguments
        """
        params = {}
        headers = headers or {}
        endpoint = "/utterances"
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def create_app(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        app_name,
        # pyre-fixme[2]: Parameter must be annotated.
        lang,
        # pyre-fixme[2]: Parameter must be annotated.
        private,
        # pyre-fixme[2]: Parameter must be annotated.
        timezone=None,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Creates a new app for an existing user.

                :param app_name: name of new app
                :param lang: language code in ISO 639-1 format
                :param private: private if true
                :param timezone: default timezone of the app
        """
        params = {}
        headers = headers or {}
        data = {"name": app_name, "lang": lang, "private": private}
        endpoint = "/apps"
        if timezone:
            params["timezone"] = timezone
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "POST",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def update_app(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        app_id,
        # pyre-fixme[2]: Parameter must be annotated.
        app_name=None,
        # pyre-fixme[2]: Parameter must be annotated.
        lang=None,
        # pyre-fixme[2]: Parameter must be annotated.
        private=None,
        # pyre-fixme[2]: Parameter must be annotated.
        timezone=None,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Updates existing app with given attributes.

                :param app_name: new_name
                :param lang: language code in ISO 639-1 format
                :param private: private if true
                :param timezone: default timezone of the app
        """
        params = {}
        headers = headers or {}
        data = {}
        endpoint = "/apps/" + quote(app_id, safe="")
        if app_name:
            data["name"] = app_name
        if lang:
            data["lang"] = lang
        if private:
            data["private"] = private
        if timezone:
            data["timezone"] = timezone
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "PUT",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp

    # pyre-fixme[3]: Return type must be annotated.
    def update_app_version(
        self,
        # pyre-fixme[2]: Parameter must be annotated.
        app_id,
        # pyre-fixme[2]: Parameter must be annotated.
        tag_name,
        # pyre-fixme[2]: Parameter must be annotated.
        new_name=None,
        # pyre-fixme[2]: Parameter must be annotated.
        desc=None,
        # pyre-fixme[2]: Parameter must be annotated.
        move_to=None,
        # pyre-fixme[2]: Parameter must be annotated.
        headers=None,
        # pyre-fixme[2]: Parameter must be annotated.
        verbose=None,
    ):
        """
        Update the tag's name or description, or move the tag to point to another tag.

                :param app_id: ID of existing app
                :param tag_name: name of existing tag
                :param new_name: name of new tag
                :param desc: new description of tag
                :param move_to: new name of tag
        """
        params = {}
        headers = headers or {}
        data = {}
        endpoint = (
            "/apps/" + quote(app_id, safe="") + "/tags/" + quote(tag_name, safe="")
        )
        if new_name:
            data["tag"] = new_name
        if desc:
            data["desc"] = desc
        if move_to:
            data["move_to"] = move_to
        if verbose:
            params["verbose"] = verbose
        resp = req(
            self.logger,
            self.access_token,
            "PUT",
            endpoint,
            params,
            json=data,
            headers=headers,
        )
        return resp
