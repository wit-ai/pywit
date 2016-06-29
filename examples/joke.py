from random import shuffle
import sys
from wit import Wit

if len(sys.argv) != 2:
    print('usage: python ' + sys.argv[0] + ' <wit-token>')
    exit(1)
access_token = sys.argv[1]

# Joke example
# See https://wit.ai/patapizza/example-joke

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

def send(request, response):
    print(response['text'])

def merge(request):
    context = request['context']
    entities = request['entities']

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

def select_joke(request):
    context = request['context']

    jokes = all_jokes[context['cat'] or 'default']
    shuffle(jokes)
    context['joke'] = jokes[0]
    return context

actions = {
    'send': send,
    'merge': merge,
    'select-joke': select_joke,
}

client = Wit(access_token=access_token, actions=actions)
client.interactive()
