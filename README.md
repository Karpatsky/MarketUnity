MarketUnity
===========

MarketUnity aims to provide a unified interface for cryptocurrency markets.

Two examples are included.  all_coins.py will scan all configured markets to
find the highest bid and lowest ask for the coins you request, and will dump
a table to stdout.  one_coin.py will look up one coin at all markets and
dump all available figures for that coin to stdout.

MarketUnity presently supports three exchanges:

* Cryptsy
  (via PyCryptsy: https://github.com/salfter/PyCryptsy)
* Bittrex
  (via python-bittrex: https://github.com/ericsomdahl/python-bittrex)
* Coins-E
  (via PyCoinsE: https://github.com/salfter/PyCoinsE)

At this time, we can retrieve a list of available markets for each exchange.
If an API call is available that will return best bid/ask, we use it;
otherwise, we retrieve the appropriate market's orderbook and get the best
bid/ask from that.  

Trading, deposits, and withdrawals aren't yet implemented.
