# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from requests import get
from wit import Wit

if len(sys.argv) != 2:
    print('usage: python ' + sys.argv[0] + ' <wit-token>')
    exit(1)
access_token = sys.argv[1]

# Celebrities example
# See https://wit.ai/aforaleka/wit-example-celebrities/


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val


def handle_message(response):
    entities = response['entities']
    greetings = first_entity_value(entities, 'greetings')
    celebrity = first_entity_value(entities, 'notable_person')
    if celebrity:
        # We can call the wikidata API using the wikidata ID for more info
        return wikidata_description(celebrity)
    elif greetings:
        return 'Hi! You can say something like "Tell me about Beyonce"'
    else:
        return "Um. I don't recognize that name. " \
                "Which celebrity do you want to learn about?"


def wikidata_description(celebrity):
    try:
        wikidata_id = celebrity['external']['wikidata']
    except KeyError:
        return 'I recognize %s' % celebrity['name']
    rsp = get('https://www.wikidata.org/w/api.php', {
        'ids': wikidata_id,
        'action': 'wbgetentities',
        'props': 'descriptions',
        'format': 'json',
        'languages': 'en'
    }).json()
    description = rsp['entities'][wikidata_id]['descriptions']['en']['value']
    return 'ooo yes I know %s -- %s' % (celebrity['name'], description)


client = Wit(access_token=access_token)
client.interactive(handle_message=handle_message)
