import ccxt.async_support as ccxt


class Trader:

    def __init__(self, args):
        if 'timeout' not in args:
            args['timeout'] = 30000
        if 'enableRateLimit' not in args:
            args['enableRateLimit'] = True

        self.exchange_id = args['exchange']
        exchange_class = getattr(ccxt, self.exchange_id)
        self.exchange = exchange_class({
            'apiKey': args['apiKey'],
            'secret': args['apiSecret'],
            'timeout': args['timeout'],
            'enableRateLimit': args['enableRateLimit']
        })

    async def get_markets(self):
        m = await self.exchange.load_markets()
        await self.exchange.close()
        return m
