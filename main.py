import asyncio
import argparse
import json

import yaml
from trader.trader import Trader


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yml', help='YAML file for configuration information')
    args = parser.parse_args()

    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    t = Trader(config)
    print(json.dumps(await t.get_markets()))

if __name__ == "__main__":
    asyncio.run(main())
