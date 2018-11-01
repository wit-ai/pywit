# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from random import shuffle
import sys
from wit import Wit

if len(sys.argv) != 2:
    print('usage: python ' + sys.argv[0] + ' <wit-token>')
    exit(1)
access_token = sys.argv[1]

# Joke example
# See https://wit.ai/aforaleka/wit-example-joke-bot

all_jokes = {
    'chuck': [
        'Chuck Norris counted to infinity - twice.',
        'Death once had a near-Chuck Norris experience.',
    ],
    'tech': [
        'Did you hear about the two antennas that got married? The ceremony was long and boring, but the reception was great!',
        'Why do geeks mistake Halloween and Christmas? Because Oct 31 === Dec 25.',
    ],
    'default': [
        'Why was the Math book sad? Because it had so many problems.',
    ],
}


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def select_joke(category):
    jokes = all_jokes[category or 'default']
    shuffle(jokes)
    return jokes[0]


def handle_message(response):
    entities = response['entities']
    get_joke = first_entity_value(entities, 'getJoke')
    greetings = first_entity_value(entities, 'greetings')
    category = first_entity_value(entities, 'category')
    sentiment = first_entity_value(entities, 'sentiment')

    if get_joke:
        return select_joke(category)
    elif sentiment:
        return 'Glad you liked it.' if sentiment == 'positive' else 'Hmm.'
    elif greetings:
        return 'Hey this is joke bot :)'
    else:
        return 'I can tell jokes! Say "tell me a joke about tech"!'


client = Wit(access_token=access_token)
client.interactive(handle_message=handle_message)
