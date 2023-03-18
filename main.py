import json
import platform
import logging
import aiohttp
import asyncio
import argparse

from tabulate import tabulate
from datetime import datetime, timedelta

BaseCurrency = ["USD", "EUR"]
BaseDays = 1

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def get_to_list_currency(data):
    return data.upper().split(',')


parser = argparse.ArgumentParser(description="The program show you exchange rates for a few day")
parser.add_argument('-c', '--currency', default=BaseCurrency)
parser.add_argument('-d', '--days', default=BaseDays)
args = vars(parser.parse_args())
if args.get('currency') != BaseCurrency:
    BaseCurrency = get_to_list_currency(args.get('currency'))
BaseDays = int(args.get('days'))


def get_urls(days: int):
    urls = []
    for day in range(days):
        data = datetime.now().date() - timedelta(days=day)
        data = datetime.strftime(data, "%d.%m.%Y")
        urls.append(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={data}')
    return urls


async def request(url: list):
    async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.info(f"Error status: {response.status} for {url}")
            except aiohttp.ClientConnectorError as err:
                logger.info(f'Connection error: {url}', str(err))


async def get_exchange():
    urls = get_urls(BaseDays)
    result = []
    for url in urls:
        result.append(request(url))
    result = await asyncio.gather(*result)
    return result


def get_output(results: list):
    output = []
    for result in results[0]:
        if result:
            one_date_exchange = {result.get('date'): {}}
            for currency in BaseCurrency:
                value = {currency: {"sale": None, "purchase": None}}
                try:
                    exchange, = list(filter(lambda el: el["currency"] == currency, result.get("exchangeRate")))
                    value[currency]["sale"] = exchange["saleRate"]
                    value[currency]["purchase"] = exchange["purchaseRate"]
                    one_date_exchange[result.get('date')].update(value)
                except ValueError:
                    logger.info(f"This {currency} currency value not found")
            output.append(one_date_exchange)
    return formatted_output_2(output)


def formatted_output(my_list):
    formatted_exchange = json.dumps(my_list, indent=4)
    return formatted_exchange


def formatted_output_2(my_list):
    table = []
    headers = ["Date", "Currency", "Sale", "Purchase"]
    table.append(headers)

    for item in my_list:
        for date, currencies in item.items():
            for currency, values in currencies.items():
                row = [date, currency, values["sale"], values["purchase"]]
                table.append(row)
    return tabulate(table, headers="firstrow")


async def main():
    now = datetime.now()
    results = await asyncio.gather(get_exchange())
    logger.info(f"Time left = {datetime.now() - now}")
    return get_output(results)


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)
