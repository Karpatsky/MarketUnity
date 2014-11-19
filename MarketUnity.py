#!/usr/bin/env python
# coding=iso-8859-1

# MarketUnity.py: unified interface to cryptocurrency markets
#
# Copyright © 2014 Scott Alfter
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
sys.path.insert(0, './PyCryptsy/')
from PyCryptsy import PyCryptsy
sys.path.insert(0, './python-bittrex/bittrex/')
from bittrex import Bittrex
sys.path.insert(0, './PyCoinsE/')
from PyCoinsE import PyCoinsE
import time
from decimal import *

class MarketUnity:

  # constructor

  def __init__(self, credentials, coins):
    self.credentials=credentials
    self.coins=coins
    self.exchanges={}
    self.last_market_update=0
    for i, exch in enumerate(self.credentials):
      self.exchanges[exch]={}
      processed=False
      if (exch=="cryptsy"):
        self.exchanges[exch]["connection"]=PyCryptsy(str(self.credentials[exch]["pubkey"]), str(self.credentials[exch]["privkey"]))
        processed=True
      if (exch=="bittrex"):
        self.exchanges[exch]["connection"]=Bittrex(str(self.credentials[exch]["pubkey"]), str(self.credentials[exch]["privkey"]))
        processed=True
      if (exch=="coins-e"):
        self.exchanges[exch]["connection"]=PyCoinsE(str(self.credentials[exch]["pubkey"]), str(self.credentials[exch]["privkey"]))
        processed=True
      if (processed==False):
        raise ValueError("unknown exchange")
    self.update_markets()

  # test if coin identifier is one we care about
  
  def check_coin_id(self, id):
    if (self.coins=={}): # null set means check all coins
      return True
    try:
      if (self.coins[id]==1):
        return True
    except:
      return False

  # get new market identifiers if they're at least one hour old

  def update_markets(self):
    if (time.time()-self.last_market_update>=3600):
      for i, exch in enumerate(self.exchanges):
        self.exchanges[exch]["markets"]={}
        markets=self.exchanges[exch]["markets"]
        conn=self.exchanges[exch]["connection"]
        if (exch=="cryptsy"):
          coindata=conn.Query("getcoindata", {})["return"]
          cm=conn.Query("getmarkets", {})["return"]
          for j, market in enumerate(cm):
            if (market["secondary_currency_code"].upper()=="BTC" and self.check_coin_id(market["primary_currency_code"].upper())):
              markets[market["primary_currency_code"].upper()]={}
              markets[market["primary_currency_code"].upper()]["id"]=int(market["marketid"])
              for k in range(0, len(coindata)):
                if (coindata[k]["code"].upper()==market["primary_currency_code"].upper()):
                  markets[market["primary_currency_code"].upper()]["healthy"]=(int(coindata[k]["maintenancemode"])==0)
        if (exch=="bittrex"):
          cm=conn.get_markets()["result"]
          for j, market in enumerate(cm):
            if (market["BaseCurrency"].upper()=="BTC" and self.check_coin_id(market["MarketCurrency"].upper())):
              markets[market["MarketCurrency"].upper()]={}
              markets[market["MarketCurrency"].upper()]["id"]=market["MarketName"]
              markets[market["MarketCurrency"].upper()]["healthy"]=market["IsActive"]
        if (exch=="coins-e"):
          cm=conn.unauthenticated_request("markets/list")["markets"]
          for j, market in enumerate(cm):
            if (market["c2"].upper()=="BTC" and self.check_coin_id(market["c1"].upper())):
              markets[market["c1"].upper()]={}
              markets[market["c1"].upper()]["id"]=market["pair"]
              markets[market["c1"].upper()]["healthy"]=(market["status"]=="healthy")
    self.last_market_update=time.time()
      
  # update prices
  
  def update_prices(self):
    for i, exch in enumerate(self.exchanges):
      conn=self.exchanges[exch]["connection"]
      if (exch=="cryptsy"):
        for j, mkt in enumerate(self.exchanges[exch]["markets"]):
          orders=conn.Query("marketorders", {"marketid": self.exchanges[exch]["markets"][mkt]["id"]})["return"]
          try:
            self.exchanges[exch]["markets"][mkt]["bid"]=Decimal(orders["buyorders"][0]["buyprice"]).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["vol"]=Decimal(0).quantize(Decimal("1.00000000"))
            for k in range(0, len(orders["buyorders"])):
              self.exchanges[exch]["markets"][mkt]["vol"]+=Decimal(orders["buyorders"][k]["total"]).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["bid_cnt"]=len(orders["buyorders"])
          except:
            self.exchanges[exch]["markets"][mkt]["bid"]=Decimal(0).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["vol"]=Decimal(0).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["bid_cnt"]=0
          try:
            self.exchanges[exch]["markets"][mkt]["ask"]=Decimal(orders["sellorders"][0]["sellprice"]).quantize(Decimal("1.00000000"))
            for k in range(0, len(orders["sellorders"])):
              self.exchanges[exch]["markets"][mkt]["vol"]+=Decimal(orders["sellorders"][k]["total"]).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["ask_cnt"]=len(orders["sellorders"])
          except:
            self.exchanges[exch]["markets"][mkt]["ask"]=Decimal(0).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["ask_cnt"]=0
      if (exch=="bittrex"):
        summ=conn.get_market_summaries()["result"]
        mkts={}
        for j, mkt in enumerate(summ):
          mkts[mkt["MarketName"]]=mkt
        for j, mkt in enumerate(self.exchanges[exch]["markets"]):
          self.exchanges[exch]["markets"][mkt]["bid"]=Decimal(mkts[self.exchanges[exch]["markets"][mkt]["id"]]["Bid"]).quantize(Decimal("1.00000000"))
          self.exchanges[exch]["markets"][mkt]["bid_cnt"]=mkts[self.exchanges[exch]["markets"][mkt]["id"]]["OpenBuyOrders"]
          self.exchanges[exch]["markets"][mkt]["ask"]=Decimal(mkts[self.exchanges[exch]["markets"][mkt]["id"]]["Ask"]).quantize(Decimal("1.00000000"))
          self.exchanges[exch]["markets"][mkt]["ask_cnt"]=mkts[self.exchanges[exch]["markets"][mkt]["id"]]["OpenSellOrders"]
          try:
            self.exchanges[exch]["markets"][mkt]["vol"]=Decimal(mkts[self.exchanges[exch]["markets"][mkt]["id"]]["BaseVolume"]).quantize(Decimal("1.00000000"))
          except:
            self.exchanges[exch]["markets"][mkt]["vol"]=Decimal(0).quantize(Decimal("1.00000000"))
      if (exch=="coins-e"):
        for j, mkt in enumerate(self.exchanges[exch]["markets"]):
          orders=conn.unauthenticated_request("market/"+self.exchanges[exch]["markets"][mkt]["id"]+"/depth")["marketdepth"]        
          try:
            self.exchanges[exch]["markets"][mkt]["bid"]=Decimal(orders["bids"][0]["r"]).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["vol"]=Decimal(0).quantize(Decimal("1.00000000"))
            for k in range(0, len(orders["bids"])):
              self.exchanges[exch]["markets"][mkt]["vol"]+=(Decimal(orders["bids"][k]["n"])*Decimal(orders["bids"][k]["q"])*Decimal(orders["bids"][k]["r"])).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["bid_cnt"]=len(orders["bids"])
          except:
            self.exchanges[exch]["markets"][mkt]["bid"]=Decimal(0).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["vol"]=Decimal(0).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["bid_cnt"]=0
          try:
            self.exchanges[exch]["markets"][mkt]["ask"]=Decimal(orders["asks"][0]["r"]).quantize(Decimal("1.00000000"))
            for k in range(0, len(orders["asks"])):
              self.exchanges[exch]["markets"][mkt]["vol"]+=(Decimal(orders["asks"][k]["n"])*Decimal(orders["asks"][k]["q"])*Decimal(orders["asks"][k]["r"])).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["ask_cnt"]=len(orders["asks"])
          except:
            self.exchanges[exch]["markets"][mkt]["ask"]=Decimal(0).quantize(Decimal("1.00000000"))
            self.exchanges[exch]["markets"][mkt]["ask_cnt"]=0

  # find best bid/ask
  
  def find_best(self):
    coins={}
    for i, ex in enumerate(self.exchanges):
      for j, cn in enumerate(self.exchanges[ex]["markets"]):
        try:
          if (coins[cn]["ask"]>self.exchanges[ex]["markets"][cn]["ask"] and self.exchanges[ex]["markets"][cn]["healthy"]):
            coins[cn]["ask"]=self.exchanges[ex]["markets"][cn]["ask"]
            coins[cn]["ask_exch"]=ex
          if (coins[cn]["bid"]<self.exchanges[ex]["markets"][cn]["bid"] and self.exchanges[ex]["markets"][cn]["healthy"]):
            coins[cn]["bid"]=self.exchanges[ex]["markets"][cn]["bid"]
            coins[cn]["bid_exch"]=ex
        except:
          if (self.exchanges[ex]["markets"][cn]["healthy"]):
            coins[cn]={}
            coins[cn]["ask"]=self.exchanges[ex]["markets"][cn]["ask"]
            coins[cn]["ask_exch"]=ex
            coins[cn]["bid"]=self.exchanges[ex]["markets"][cn]["bid"]
            coins[cn]["bid_exch"]=ex
    return coins

