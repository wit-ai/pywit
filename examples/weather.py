from wit import Wit

# Weather example
# See https://wit.ai/patapizza/example-weather

access_token = 'YOUR_ACCESS_TOKEN'

def say(session_id, msg):
  print(msg)

def merge(context, entities):
  return context

def error(session_id, msg):
  print('Oops, I don\'t know what to do.')

def fetch_forecast(context):
  context['forecast'] = 'cloudy'
  return context

actions = {
    'say': say,
    'merge': merge,
    'error': error,
    'fetch-forecast': fetch_forecast,
    }
client = Wit(access_token, actions)

session_id = 'my-user-id-42'
client.run_actions(session_id, 'weather in London', {})
