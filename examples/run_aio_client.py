import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://python.org') as resp:
            print('status', resp.status)
            print('content-type', resp.headers['content-type'])
            html = await resp.text()
            print('body', html[:15], '...')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
