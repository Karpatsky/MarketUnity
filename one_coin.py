#!/usr/bin/env python

from MarketUnity import MarketUnity
import json
import pprint
import time
import texttable
import sys

creds=json.loads(open("credentials.json").read())
coins={}
coins[sys.argv[1]]=1
u=MarketUnity(creds, coins)

u.update_prices()

tbl=texttable.Texttable(0)
tbl.header(["exch", "bid", "bid_cnt", "ask", "ask_cnt", "spread", "vol", "healthy"])
tbl.set_cols_dtype(["t", "f", "i", "f", "i", "f", "f", "t"])
tbl.set_precision(8)
tbl.set_deco(0)
for i, e in enumerate(u.exchanges):
  try:
    tbl.add_row([e, u.exchanges[e]["markets"][sys.argv[1].upper()]["bid"], u.exchanges[e]["markets"][sys.argv[1].upper()]["bid_cnt"], u.exchanges[e]["markets"][sys.argv[1].upper()]["ask"], u.exchanges[e]["markets"][sys.argv[1].upper()]["ask_cnt"], u.exchanges[e]["markets"][sys.argv[1].upper()]["ask"]-u.exchanges[e]["markets"][sys.argv[1].upper()]["bid"], u.exchanges[e]["markets"][sys.argv[1].upper()]["vol"], u.exchanges[e]["markets"][sys.argv[1].upper()]["healthy"] ])
  except:
    pass
print tbl.draw()
