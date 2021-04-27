import copy
import time
import logging
import asyncio
from threading import Thread

import ccxt.async_support as ccxt


class Trader(Thread):

    def __init__(self, args={}):
        Thread.__init__(self)
        self._loop = asyncio.new_event_loop()
        if args == {}:
            return
        if 'timeout' not in args:
            args['timeout'] = 30000
        if 'enableRateLimit' not in args:
            args['enableRateLimit'] = True
        if 'sandboxMode' not in args:
            args['sandboxMode'] = False
        if 'apiPassword' not in args:
            args['apiPassword'] = ''

        self._exchange_id = args['exchange']
        exchange_class = getattr(ccxt, self._exchange_id)

        self.exchange = exchange_class({
            'apiKey': args['apiKey'],
            'secret': args['apiSecret'],
            'password': args['apiPassword'],
            'timeout': args['timeout'],
            'enableRateLimit': args['enableRateLimit'],
            'rateLimit': args['rateLimit'],
            'options': {
                'createMarketBuyOrderRequiresPrice': False
            }, 
            'asyncio_loop': self._loop
        })
        self._symbol_str = args['symbols'][0]
        self._base = self._symbol_str.split('/')[0]
        self._quote = self._symbol_str.split('/')[1]
        self._sandboxMode = args['sandboxMode']
        self._targetAmount = args['targetAmount']
        self._gridSize = args['gridSize']
        self._lowerLimit = args['lowerLimit']
        self._shouldGatherData = True
        self._shouldRun = True
        self._orders = []
        self._balance = {}
        self._ticker = 1
        self._markets = {}
        self._state = 'running'
        

    @property
    def markets(self):
        return self._markets

    @property
    def symbol(self):
        return self._symbol_str

    @property
    def balance(self):
        return self._balance

    @property
    def state(self):
        return self._state

    @property
    def orders(self):
        return self._orders

    def shouldRun(self, shouldRun):
        self._shouldRun = shouldRun

    def shouldGatherData(self, shouldGatherData):
        self._shouldGatherData = shouldGatherData

    def sandboxMode(self, sandboxMode):
        self._sandboxMode = sandboxMode

    def params(self, args):
        if 'symbol' in args:
            self._symbol_str = args['symbol']
            self._base = self._symbol_str.split('/')[0]
            self._quote = self._symbol_str.split('/')[1]
        if 'target' in args:
            self._targetAmount = args['target']
        if 'grid_size' in args:
            self._gridSize = args['grid_size']
        if 'limit' in args:
            self._lowerLimit = args['limit']

    async def prepare(self):
        logging.info('Loading markets and symbols...')
        self._markets = await self.exchange.load_markets()
        self._orders = await self.exchange.fetchMyTrades(self._symbol_str)

        logging.info("Loading funds...")
        self._balance = await self.exchange.fetch_balance()
        logging.info('Ready to trade!')
        await self.close()

    async def close(self):
        if hasattr(self, 'exchange'):
            await self.exchange.close()
        else:
            return


    async def gatherData(self):
        # Update data
        orders = []
        for o in self._orders:
            if (not self._sandboxMode):
                if('order' in o):
                    newo = await self.exchange.fetchOrder(o['order'])
                else:
                    newo = await self.exchange.fetchOrder(o['id'])
                orders.append(newo)
            else:
                orders.append(o)
        self._orders = orders

        # Don't ask the exchange for our balance in sandbox mode after the first time
        if (not self._sandboxMode and self._balance != {}):
            self._balance = (await self.exchange.fetch_balance())['total']

        orderbook = await self.exchange.fetch_order_book(self._symbol_str)
        spread = orderbook['asks'][0][0] - orderbook['bids'][0][0]
        mprice = orderbook['bids'][0][0] + (spread / 2)
                
        if self._base not in self._balance:
            self._balance[self._base] = 0
            self._baseBalance = 0
        else:
            self._baseBalance = self._balance[self._base]
        if self._quote not in self._balance:
            self._balance[self._quote] = 0
            self._quoteBalance = 0
        else:
            self._quoteBalance = self._balance[self._quote]
        logging.info(f'Balances: {self._baseBalance} {self._base}, {self._quoteBalance} {self._quote}; Total portfolio value is {self._quoteBalance + self._baseBalance * mprice} {self._quote}')
        logging.info(f'{self._symbol_str} price is {mprice}, {self._base} value is {self._baseBalance * mprice} {self._quote}')

        return mprice

    
    async def createOrder(self, side, price):
        amount = abs(self._targetAmount - (self._baseBalance * price)) / price
        if side == 'buy':
            samount = amount * price
            sufficient = samount > self._quoteBalance
            cur = self._quote
            bal = self._quoteBalance
        elif side == 'sell':
            samount = amount
            sufficient = samount > self._baseBalance
            cur = self._base
            bal = self._baseBalance

        if sufficient:
            logging.warn(f'Wanted to {side} {amount} {self._symbol_str}, but had insufficient funds. Needed {samount} {cur} and had {bal} {cur}')
            return

        if (not self._sandboxMode):
            order = await self.exchange.create_order(self._symbol_str, 'market', side, amount, price)
        else:
            order = {'status': 'sandbox', 'side': side, 'cost': amount * price, 'symbol': self._symbol_str, 'price': price, 'amount': amount}
            self._balance['total'][self._base] += amount
            self._balance['total'][self._quote] -= amount * price

        self._orders.append(order)
        logging.info(f'Completed {side} of {order["amount"]} {self._symbol_str} for {order["price"]}')
        if(order["amount"] != amount or order['price'] != price):
            logging.warn(f'Actual {side} did not match expected {side} of {amount} {self._symbol_str} at {price}')

    
    async def trade(self):
        if self._markets == {}:
            await self.prepare()

        while(self._shouldGatherData):
            try:
                mprice = await self.gatherData()

                if(self._shouldRun):
                    # Skip if balance == target balance
                    if (self._baseBalance * mprice == self._targetAmount):
                        self._state = 'waiting'
                        logging.info(f'{self._base} balance is {self._baseBalance} at {mprice}, {self._state}')
                        continue

                    # Skip if balance is at or below lowerLimit
                    if (mprice <= self._lowerLimit):
                        self._state = 'waiting'
                        logging.info(f'{self._base} price is less than threshold of {self._lowerLimit}, {self._state}')
                        continue

                    # Sell if price rises by gridSize% over target balance
                    if (self._baseBalance * mprice >= self._targetAmount + (self._targetAmount * self._gridSize)):
                        self._state = 'running'
                        await self.createOrder('sell', mprice)
                        continue
                    
                    # Buy if price drops by gridSize% over target balance or balance is out of whack
                    if(self._baseBalance * mprice <= self._targetAmount - (self._targetAmount * self._gridSize)):
                        self._state = 'running'
                        await self.createOrder('buy', mprice)
                        continue
                    
                    else:
                        self._state = 'waiting'
                        logging.info(f'{self._base} value is within {self._gridSize * 100}% of {self._targetAmount} {self._quote}, {self._state}.')
                        continue

                self._state = 'stopped'
                logging.info(f'Trader is {self._state}')
            except (ccxt.ExchangeError, ccxt.NetworkError) as e:
                logging.error(f'{e}')

        await self.close()

    def run(self):
        self._loop.run_until_complete(self.trade())
