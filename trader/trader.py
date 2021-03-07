import copy
import time
import logging

import ccxt.async_support as ccxt


class Trader:

    def __init__(self, args):
        if 'timeout' not in args:
            args['timeout'] = 30000
        if 'enableRateLimit' not in args:
            args['enableRateLimit'] = True
        if 'symbols' not in args or not args['symbols']:
            args['symbols'] = ['BTC/USDT', 'LTC/USDT']
        if 'sandboxMode' not in args:
            args['sandboxMode'] = False

        self._exchange_id = args['exchange']
        exchange_class = getattr(ccxt, self._exchange_id)

        self.exchange = exchange_class({
            'apiKey': args['apiKey'],
            'secret': args['apiSecret'],
            'timeout': args['timeout'],
            'enableRateLimit': args['enableRateLimit'],
            'rateLimit': args['rateLimit'],
            'nonce': lambda: int(time.time() * 1000)
        })
        self._symbols_str = args['symbols']
        self._sandboxMode = args['sandboxMode']
        self._baseAmount = args['baseAmount']
        self._markets = {}
        self._symbols = []
        self._balance = {}

    @property
    def markets(self):
        return self._markets

    @property
    def symbols(self):
        return self._symbols

    @property
    def balance(self):
        return self._balance

    async def prepare(self):
        logging.info('Loading markets and symbols...')
        self._markets = await self.exchange.load_markets()
        for s in self._symbols_str:
            self.symbols.append(self.exchange.markets[s])

        logging.info("Loading funds...")
        self._balance = await self.exchange.fetch_balance()
        logging.info('Available funds for trading:')
        for i in self._balance['free']:
            logging.info(f"{i}: {self._balance['free'][i]}")
        logging.info('Funds held or otherwise unavailable:')
        for i in self._balance['used']:
            logging.info(f"{i}: {self._balance['used'][i]}")
        logging.info('Ready to trade!')
        await self.close()

    async def close(self):
        await self.exchange.close()

    async def find_opportunities(self):
        symbols = copy.deepcopy(self.symbols)
        for s in symbols:
            orderbook = await self.exchange.fetch_order_book(s['symbol'])
            s['bid'] = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
            s['ask'] = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
            s['spread'] = (s['ask'] - s['bid']) if (s['bid'] and s['ask']) else None

        # Trade Path 1: Buy - Buy - Sell
        cr1 = (1 / symbols[0]['ask']) * (1 / symbols[1]['ask']) * symbols[2]['bid']

        # Trade Path 2: Buy - Sell - Sell
        cr2 = (1 / symbols[2]['ask']) * (symbols[1]['bid']) * symbols[0]['bid']

        await self.close()
        logging.debug(f"Cross-rates for {symbols[0]['symbol']}->{symbols[1]['symbol']}->{symbols[2]['symbol']} --- trade path 1: {cr1} trade path 2: {cr2}")
        return cr1, cr2

    async def trade(self):
        cr1, cr2 = await self.find_opportunities()
        magic = 1.006  # 1 + 0.2% * 3 trades
        if cr1 < magic and cr2 < magic:
            logging.debug(f'Cross rates below threshold of {magic}, skipping.')
            return

        prices = []
        for s in self.symbols[:-1]:
            price = await self.exchange.fetch_order_book(s['symbol'])
            prices.append({'ask': price['asks'][0][0], 'bid': price['asks'][0][0]})
        price = await self.exchange.fetch_order_book(self.symbols[-1]['symbol'])
        prices.append({'ask': price['asks'][0][0], 'bid': price['asks'][0][0]})

        await self.close()

        # Buy - Buy - Sell
        if cr1 > magic:
            # TODO fix these calculations
            symbol2_num = self._baseAmount / prices[1]['ask']
            final_num = symbol2_num * prices[2]['bid']
            if not self._sandboxMode and self.exchange.has['createMarketOrder']:
                await self.exchange.create_order(self.symbols[0]['symbol'], 'market', 'buy', self._baseAmount)
                await self.exchange.create_order(self.symbols[1]['symbol'], 'market', 'buy', symbol2_num)
                await self.exchange.create_order(self.symbols[2]['symbol'], 'market', 'sell', final_num)
            if not self.exchange.has['createMarketOrder']:
                logging.warning(f'Exchange {self._exchange_id} does not support market orders. Skipping Buy->Buy->Sell trade path.')
            else:
                logging.info(f"Buy->Buy->Sell trade path executed for {self.symbols[0]['symbol']}->{self.symbols[1]['symbol']}->{self.symbols[2]['symbol']}: Start Value {self._baseAmount} End Value {final_num}")

        # Buy - Sell - Sell
        elif cr2 > magic:
            # TODO fix these calculations
            symbol2_num = self._baseAmount / prices[0]['ask']
            final_num = symbol2_num * prices[2]['bid']
            if not self._sandboxMode and self.exchange.has['createMarketOrder']:
                await self.exchange.create_order(self.symbols[0]['symbol'], 'market', 'buy', self._baseAmount)
                await self.exchange.create_order(self.symbols[1]['symbol'], 'market', 'sell', symbol2_num)
                await self.exchange.create_order(self.symbols[2]['symbol'], 'market', 'sell', final_num)
            if not self.exchange.has['createMarketOrder']:
                logging.warning(f'Exchange {self.exchange_id} does not support market orders. Skipping Buy->Sell->Sell trade path.')
            else:
                logging.info(f"Trade path 2 executed for {self.symbols[0]['symbol']}-{self.symbols[1]['symbol']}-{self.symbols[2]['symbol']}: Start Value {self._baseAmount} End Value {final_num}")
            return
