#!/usr/bin/env python

from MarketUnity import MarketUnity
import json
import pprint
import time
import pprint
import texttable
import sys

creds=json.loads(open("credentials.json").read())
coins=json.loads(open("coins.json").read())
u=MarketUnity(creds, coins)
#pprint.pprint(u.exchanges)
#sys.exit()

u.update_prices()
coins=u.find_best()

tbl=texttable.Texttable()
tbl.header(["coin", "best_bid", "best_bid_exch", "best_ask", "best_ask_exch"])
tbl.set_cols_dtype(["t", "f", "t", "f", "t"])
tbl.set_precision(8)
tbl.set_deco(0)
for i, cn in enumerate(sorted(coins)):
  tbl.add_row([cn, coins[cn]["bid"], coins[cn]["bid_exch"], coins[cn]["ask"], coins[cn]["ask_exch"] ])
print tbl.draw()
