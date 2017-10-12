from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from wit import Wit

if len(sys.argv) != 2:
    print('usage: python ' + sys.argv[0] + ' <wit-token>')
    exit(1)
access_token = sys.argv[1]

def send(request, response):
    print(response['text'])

actions = {
    'send': send,
}

client = Wit(access_token=access_token, actions=actions)
print(client.message('what is temperature', None, 2, True))
