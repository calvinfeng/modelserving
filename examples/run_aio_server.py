from aiohttp import web


async def handle(request):
    name = request.match_info.get('name', 'Anonymous')
    text = 'Hello, ' + name
    return web.Response(text=text)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle),
        web.get('/{name}', handle)
    ])
    web.run_app(app, port=8888)