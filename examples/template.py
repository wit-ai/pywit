import sys
from wit import Wit

if len(sys.argv) != 2:
    print("usage: python examples/template.py <wit-token>")
    exit(1)
access_token = sys.argv[1]

def say(session_id, context, msg):
    print(msg)

def merge(session_id, context, entities, msg):
    return context

def error(session_id, context, e):
    print(str(e))

actions = {
    'say': say,
    'merge': merge,
    'error': error,
}
client = Wit(access_token, actions)

session_id = 'my-user-id-42'
client.run_actions(session_id, 'your message', {})
