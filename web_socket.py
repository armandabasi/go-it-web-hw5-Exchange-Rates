import json
import asyncio
import logging
from aiofile import async_open
from aiopath import AsyncPath
import websockets
import names
from datetime import datetime
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from main_socket import get_exchange_output, formatted_output_2
from prettytable import PrettyTable

logging.basicConfig(level=logging.INFO)
FILE_NAME = 'data.json'
STORAGE_FILE = AsyncPath(FILE_NAME)


async def logging_data(massage, user):
    time_to_get = str(datetime.now())
    data = {}
    if await STORAGE_FILE.exists():
        async with async_open(STORAGE_FILE, 'r', encoding='utf-8') as afd:
            data = await afd.read()
            data = json.loads(data)
        if user not in data:
            data[user] = {}
        data[user][time_to_get] = massage
    else:
        data[user] = {time_to_get: massage}
    async with async_open(STORAGE_FILE, 'w', encoding='utf-8') as afd:
        await afd.write(json.dumps(data, indent=4, ensure_ascii=False))


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def convert_to_table(self, data) -> str:
        table = PrettyTable()
        table.field_names = ["Date", "Currency", "Sale", "Purchase"]
        for rate in data:
            for date, currencies in rate.items():
                for currency, rates in currencies.items():
                    table.add_row([date, currency, rates["sale"], rates["purchase"]])
        return table.get_html_string()

    async def send_table_to_clients(self, table_data):
        if self.clients:
            [await client.send(table_data) for client in self.clients]

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                await self.send_to_clients(f"{ws.name}: {message}")
                days = 1
                if message != "exchange":
                    message, days = message.split()
                r = await get_exchange_output(int(days))
                table_data = await self.convert_to_table(r)
                await self.send_table_to_clients(table_data)
                await logging_data(r, ws.name)

            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
