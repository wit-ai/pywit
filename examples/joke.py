from random import shuffle
import sys
from wit import Wit

# Joke example
# See https://wit.ai/patapizza/example-joke

if len(sys.argv) != 2:
    print("usage: python examples/joke.py <wit-token>")
    exit(1)
access_token = sys.argv[1]

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
        'Why was the Math book sad? Because it had so many problems.',
    ],
}

def say(session_id, context, msg):
    print(msg)

def merge(session_id, context, entities, msg):
    if 'joke' in context:
        del context['joke']
    category = first_entity_value(entities, 'category')
    if category:
        context['cat'] = category
    sentiment = first_entity_value(entities, 'sentiment')
    if sentiment:
        context['ack'] = 'Glad you liked it.' if sentiment == 'positive' else 'Hmm.'
    elif 'ack' in context:
        del context['ack']
    return context

def error(session_id, context, e):
    print(str(e))

def select_joke(session_id, context):
    jokes = all_jokes[context['cat'] or 'default']
    shuffle(jokes)
    context['joke'] = jokes[0]
    return context

actions = {
    'say': say,
    'merge': merge,
    'error': error,
    'select-joke': select_joke,
}
client = Wit(access_token, actions)

session_id = 'my-user-id-42'
client.run_actions(session_id, 'tell me a joke about tech', {})
