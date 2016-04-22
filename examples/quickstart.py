from wit import Wit
import sys

# Quickstart example
# See https://wit.ai/l5t/Quickstart

if len(sys.argv) != 2:
  print(sys.argv)
  print("usage: python examples/quickstart.py <wit-token>")
  exit(1)
access_token = sys.argv[1]

def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def say(session_id, context, msg):
    print(msg)

def merge(session_id, context, entities, msg):
    loc = first_entity_value(entities, 'location')
    if loc:
        context['loc'] = loc
    return context

def error(session_id, context, e):
    print(str(e))

def fetch_weather(session_id, context):
    context['forecast'] = 'sunny'
    return context

actions = {
    'say': say,
    'merge': merge,
    'error': error,
    'fetch-weather': fetch_weather,
}

client = Wit(access_token, actions)
client.interactive()
