#!/usr/bin/env python
# encoding: utf-8
# 阅读笔记
import sys
from wit import Wit

# debug
import logging
LOG_FILE = "/tmp/log_file.log"
logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler=logging.FileHandler(LOG_FILE)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

if len(sys.argv) != 2:
    print('usage: python ' + sys.argv[0] + ' <wit-token>')
    exit(1)
access_token = sys.argv[1]

# Quickstart example
# See https://wit.ai/ar7hur/Quickstart

def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    print(response['text'])

def get_forecast(request):
    context = request['context']
    entities = request['entities']

    loc = first_entity_value(entities, 'location')
    if loc:
        context['forecast'] = 'sunny'
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']

    return context

actions = {
    'send': send,
    'getForecast': get_forecast,
}

client = Wit(access_token=access_token, actions=actions,logger=logger) # 研究入口
client.interactive() # 用户输入，跟踪过去, What's the weather in Rome?
