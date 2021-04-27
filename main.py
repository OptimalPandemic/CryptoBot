import asyncio
import argparse
import logging

import yaml
from trader.trader import Trader

t = Trader()

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    logging.info('Starting up.....')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yml', help='YAML file for configuration information')
    args = parser.parse_args()

    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    t = Trader(config)
    await t.prepare()
    await t.run()
    await t.close()

async def close():
    await t.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(close())
        logging.info("Stopping.....")
