# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.


import sys

from requests import get
from wit import Wit

if len(sys.argv) != 2:
    print("usage: python " + sys.argv[0] + " <wit-token>")
    exit(1)
access_token = sys.argv[1]

# Celebrities example
# See https://wit.ai/aleka/wit-example-celebrities/


def first_entity_resolved_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]
    if "resolved" not in val:
        return None
    val = val["resolved"]["values"][0]
    if not val:
        return None
    return val


def first_trait_value(traits, trait):
    if trait not in traits:
        return None
    val = traits[trait][0]["value"]
    if not val:
        return None
    return val


def handle_message(response):
    greetings = first_trait_value(response["traits"], "wit$greetings")
    celebrity = first_entity_resolved_value(
        response["entities"], "wit$notable_person:notable_person"
    )
    if celebrity:
        # We can call the wikidata API using the wikidata ID for more info
        return wikidata_description(celebrity)
    elif greetings:
        return 'Hi! You can say something like "Tell me about Beyonce"'
    else:
        return (
            "Um. I don't recognize that name. "
            "Which celebrity do you want to learn about?"
        )


def wikidata_description(celebrity):
    try:
        wikidata_id = celebrity["external"]["wikidata"]
    except KeyError:
        return "I recognize %s" % celebrity["name"]
    rsp = get(
        "https://www.wikidata.org/w/api.php",
        {
            "ids": wikidata_id,
            "action": "wbgetentities",
            "props": "descriptions",
            "format": "json",
            "languages": "en",
        },
    ).json()
    description = rsp["entities"][wikidata_id]["descriptions"]["en"]["value"]
    return "ooo yes I know {} -- {}".format(celebrity["name"], description)


client = Wit(access_token=access_token)
client.interactive(handle_message=handle_message)
