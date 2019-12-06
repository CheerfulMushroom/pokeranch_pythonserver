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
        app.router.add_route('POST', '/logout', Handler.logout)
        app.router.add_route('POST', '/add_pokemon', Handler.add_pokemon)
        app.router.add_route('POST', '/save_pokemon', Handler.save_pokemon)
        app.router.add_route('GET', '/get_pokemon', Handler.get_pokemon)

        app.router.add_route('POST', '/test', Handler.test)

        web.run_app(app, port=self._port)


class Handler:
    @staticmethod
    async def auth(request: web.Request):
        data = await request.json()
        login = data.get('login', None)
        password = data.get('password', None)

        db_service = DBService()
        if '@' in login:
            token = db_service.auth(mail=login, password=password)
        else:
            token = db_service.auth(login=login, password=password)

        if token is None:
            return web.json_response({'error_string': 'Invalid auth credentials'}, status=401)

        return web.json_response({'token': token})

    @staticmethod
    async def register(request: web.Request):
        data = await request.json()
        login = data.get('login', None)
        mail = data.get('mail', None)
        password = data.get('password', None)

        if data is None or login is None or mail is None:
            return web.json_response({'error_string': "Not enough arguments"}, status=400)

        if '@' not in mail:
            return web.json_response({'error_string': "Mail doesn't have '@' in it"}, status=400)

        if '@' in login:
            return web.json_response({'error_string': "Login has '@' in it"}, status=400)

        db_service = DBService()
        if db_service.create_user(login=login, mail=mail, password=password):
            return web.json_response({})
        return web.json_response({'error_string': "User with such login or mail already exists"}, status=401)

    @staticmethod
    async def get_profile(request: web.Request):
        data = await request.json()
        login = data.get('login', None)

        if login is None:
            return web.json_response({'error_string': 'No login found'}, status=400)

        db_service = DBService()
        user_exists = db_service.has_user(login=login)
        # TODO(al): debug
        return web.json_response({'exist': user_exists})

    @staticmethod
    async def logout(request: web.Request):
        data = await request.json()
        token = data.get('token', None)

        if token is None:
            return web.json_response({'error_string': 'No token found'}, status=400)

        db_service = DBService()
        db_service.logout(token)
        return web.json_response()

    @staticmethod
    async def add_pokemon(request: web.Request):
        data = await request.json()
        token = data.get('token', None)
        if token is None:
            return web.json_response({'error_string': 'No token found'}, status=400)

        db_service = DBService()
        if db_service.add_pokemon(data):
            return web.json_response()
        return web.json_response({'error_string': 'Wrong data or not enough data'}, status=400)

    @staticmethod
    async def save_pokemon(request: web.Request):
        data = await request.json()
        token = data.get('token', None)
        if token is None:
            return web.json_response({'error_string': 'No token found'}, status=400)

        db_service = DBService()
        if db_service.save_pokemon(data):
            return web.json_response()
        return web.json_response({'error_string': 'Wrong data or not enough data'}, status=400)

    @staticmethod
    async def get_pokemon(request: web.Request):
        data = await request.json()
        token = data.get('token', None)
        if token is None:
            return web.json_response({'error_string': 'No token found'}, status=400)

        db_service = DBService()
         # TODO(al) check token
        if db_service.get_pokemon(data):
            return web.json_response()
        return web.json_response({'error_string': 'Wrong data or not enough data'}, status=400)

    @staticmethod
    async def test(request: web.Request):
        db_service = DBService()

        return web.json_response({"result": db_service.get_user_id(token='adasad')})
