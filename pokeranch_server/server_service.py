from aiohttp import web, WSCloseCode
import asyncio
import json


class Server:
    def __init__(self, port=None):
        self.port = port or 8888

    @staticmethod
    async def on_shutdown(app):
        for ws in set(app['websockets']):
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    @staticmethod
    async def listen(request: web.Request):
        addr = request.host
        print(f"Connected: {addr}")
        try:
            data = await request.json()
        except Exception as e:
            error_message = f'Couldn\'t parse json: {e}'
            print(error_message)
            return web.Response(body=json.dumps({'error_message': error_message}), status=400)

        if 'action' not in data:
            error_message = f'No action found'
            print(error_message)
            return web.Response(body=json.dumps({'error_message': error_message}), status=400)

        action = data['action']

        if action == 'authorize':
            pass
        elif action == 'save':
            pass
        elif action == 'get_info':
            pass
        else:
            error_message = f'No such action: {action}'
            print(error_message)
            return web.Response(body=json.dumps({'error_message': error_message}), status=400)

    def start(self):
        app = web.Application()
        app.router.add_route('GET', '/', self.listen)
        app.router.add_route('POST', '/', self.listen)

        app.on_shutdown.append(self.on_shutdown)

        web.run_app(app)
