import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.backend.backend.settings')
from web.backend.crypto.models import Asset, Order, Setting
import asyncio
import argparse
import logging

import yaml
from trader.trader import Trader
from constance import config


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting up.....')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yml', help='YAML file for configuration information')
    args = parser.parse_args()

    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    t = Trader(config)
    await t.prepare()

    while True:
        # Check we're still allowed to trade
        t.shouldRun(config.enabled)
        if not t.shouldRun(shouldRun):
            continue

        # Set sandbox mode
        t.sandboxMode(config.sandboxMode)

        await t.trade()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stopping.....")
