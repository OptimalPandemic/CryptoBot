import asyncio
import argparse
import logging

import yaml
from trader.trader import Trader


async def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='trader.log', encoding='utf-8', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yml', help='YAML file for configuration information')
    args = parser.parse_args()

    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    t = Trader(config)
    await t.prepare()
    while True:
        logging.info('Checking:')
        cr1, cr2 = await t.find_opportunities()
        logging.info(f'Path A: {cr1} Path B: {cr2}')

if __name__ == "__main__":
    asyncio.run(main())
