import asyncio
import argparse
import logging

import yaml
from trader.trader import Trader


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
        await t.trade()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stopping.....")
