import copy

import ccxt.async_support as ccxt


class Trader:

    markets = {}
    symbols = []
    symbols_str = []

    def __init__(self, args):
        if 'timeout' not in args:
            args['timeout'] = 30000
        if 'enableRateLimit' not in args:
            args['enableRateLimit'] = True
        if 'symbols' not in args or not args['symbols']:
            args['symbols'] = ['BTC/USDT', 'LTC/USDT']

        self.exchange_id = args['exchange']
        exchange_class = getattr(ccxt, self.exchange_id)
        self.exchange = exchange_class({
            'apiKey': args['apiKey'],
            'secret': args['apiSecret'],
            'timeout': args['timeout'],
            'enableRateLimit': args['enableRateLimit']
        })
        self.symbols_str = args['symbols']

    async def prepare(self):
        self.markets = await self.exchange.load_markets()
        for s in self.symbols_str:
            self.symbols.append(self.exchange.markets[s])
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

        # Buy - Buy - Sell
        cr1 = (1 / symbols[0]['ask']) * (1 / symbols[1]['ask']) * symbols[2]['bid']

        # Buy - Sell - Sell
        cr2 = (1 / symbols[2]['ask']) * (symbols[1]['bid']) * symbols[0]['bid']

        await self.close()
        return cr1, cr2

