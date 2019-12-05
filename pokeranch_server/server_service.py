from aiohttp import web, WSCloseCode
import json


@web.middleware
async def json_check(request, handler):
    try:
        await request.json()
    except Exception as e:
        error_message = f'Couldn\'t parse json: {e}'
        print(error_message)
        return web.Response(body=json.dumps({'error_message': error_message}), status=400)
    return await handler(request)


@web.middleware
async def log_host(request, handler):
    addr = request.host
    print(f"Connected: {addr}")
    return await handler(request)


class Server:
    def __init__(self, port=None):
        self.port = port or 8888

    @staticmethod
    async def on_shutdown(app):
        for ws in set(app['websockets']):
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    def start(self):
        app = web.Application(middlewares=[log_host, json_check])
        app.router.add_route('POST', '/auth', Handler.auth)
        app.router.add_route('GET', '/get_profile', Handler.get_profile)
        app.router.add_route('POST', '/save', Handler.save)

        app.on_shutdown.append(self.on_shutdown)

        web.run_app(app)


class Handler:
    @staticmethod
    async def auth(request: web.Request):
        return web.Response(body='auth')

    @staticmethod
    async def save(request: web.Request):
        return web.Response(body='save')

    @staticmethod
    async def get_profile(request: web.Request):
        return web.Response(body='get_profile')

