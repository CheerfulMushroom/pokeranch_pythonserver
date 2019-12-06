from aiohttp import web, WSCloseCode
from pokeranch_server.db_service import DBService
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
        self._port = port or 8888

    @staticmethod
    async def on_shutdown(app):
        for ws in set(app['websockets']):
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    def start(self):
        app = web.Application(middlewares=[log_host, json_check])
        app.router.add_route('POST', '/auth', Handler.auth)
        app.router.add_route('POST', '/register', Handler.register)
        app.router.add_route('GET', '/get_profile', Handler.get_profile)
        app.router.add_route('POST', '/save', Handler.save)

        app.on_shutdown.append(self.on_shutdown)

        web.run_app(app, port=self._port)


class Handler:
    @staticmethod
    async def auth(request: web.Request):
        data = await request.json()
        login = str(data.get('login', None))
        password = data.get('password', None)

        db_service = DBService()
        if '@' in login:
            user_exists = db_service.auth(mail=login, password=password)
        else:
            user_exists = db_service.auth(login=login, password=password)

        if user_exists:
            token = db_service.generate_token()
            return web.json_response({'token': token})

        return web.json_response({'error_string': 'Invalid auth credentials'}, status=401)

    @staticmethod
    async def register(request: web.Request):
        data = request.json()
        db_service = DBService()
        if db_service.register_profile('keke', 'kjajsdljas', 'asjdga'):
            return web.json_response({'registered': True})
        return web.json_response({'registered': False})

    @staticmethod
    async def save(request: web.Request):
        data = request.json()
        db_service = DBService()
        return web.Response(body='save' + str(db_service.has_user_by_login('keke')))

    @staticmethod
    async def get_profile(request: web.Request):
        data = request.json()
        db_service = DBService()
        return web.Response(body='get_profile')
