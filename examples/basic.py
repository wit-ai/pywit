# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from wit import Wit

if len(sys.argv) != 2:
    print("usage: python " + sys.argv[0] + " <wit-token>")
    exit(1)
access_token = sys.argv[1]

client = Wit(access_token=access_token)
client.interactive()
