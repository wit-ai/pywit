# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.


import sys

from wit import Wit

if len(sys.argv) != 2:
    print("usage: python " + sys.argv[0] + " <wit-token>")
    exit(1)
access_token = sys.argv[1]

client = Wit(access_token=access_token)
client.interactive()
