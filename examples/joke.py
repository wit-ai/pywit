from random import shuffle
from wit import Wit

# Joke example
# See https://wit.ai/patapizza/example-joke

access_token = 'YOUR_ACCESS_TOKEN'


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

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
        'Why was the Math book sad? Because it had so many problems.'
    ],
}


def say(session_id, msg):
    print(msg)


def merge(context, entities):
    new_context = dict(context)
    if 'joke' in new_context:
        del new_context['joke']
    category = first_entity_value(entities, 'category')
    if category:
        new_context['cat'] = category
    sentiment = first_entity_value(entities, 'sentiment')
    if sentiment:
        new_context['ack'] = 'Glad you liked it.' if sentiment == 'positive' else 'Hmm.'
    elif 'ack' in new_context:
        del new_context['ack']
    return new_context


def error(session_id, msg):
    print('Oops, I don\'t know what to do.')


def select_joke(context):
    new_context = dict(context)
    jokes = all_jokes[new_context['cat'] or 'default']
    shuffle(jokes)
    new_context['joke'] = jokes[0]
    return new_context

actions = {
    'say': say,
    'merge': merge,
    'error': error,
    'select-joke': select_joke,
}
client = Wit(access_token, actions)

session_id = 'my-user-id-42'
client.run_actions(session_id, 'tell me a joke about tech', {})
