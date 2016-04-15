from wit import Wit

# Quickstart example
# See https://wit.ai/l5t/Quickstart

access_token = 'YOUR_ACCESS_TOKEN'


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def say(session_id, msg):
    print(msg)


def merge(session_id, context, entities, msg):
    new_context = dict(context)
    loc = first_entity_value(entities, 'location')
    if loc:
        new_context['loc'] = loc
    return new_context


def error(session_id, context):
    print('Oops, I don\'t know what to do.')


def fetch_weather(session_id, context):
    new_context = dict(context)
    new_context['forecast'] = 'sunny'
    return new_context

actions = {
    'say': say,
    'merge': merge,
    'error': error,
    'fetch-weather': fetch_weather,
}
client = Wit(access_token, actions)

session_id = 'my-user-id-42'
client.run_actions(session_id, 'weather in London', {})
