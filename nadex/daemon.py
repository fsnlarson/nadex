#!/usr/bin/env python
from __future__ import print_function

import rethinkdb

from nadex import NadexRestApi

"""
Nadex Daemon

1. establish connection
2. cache meta data
3. maintain tables of lightstreamer
4. forward the stream to Kafka


market,
  instrument
    timeseries
      contract  NB.<Daily|Weekly>.<symbol>.OPT-
"""

client = NadexRestApi()
client.Account.login()


