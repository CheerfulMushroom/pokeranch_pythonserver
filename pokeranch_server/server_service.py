from aiohttp import web, WSCloseCode
from pokeranch_server.db_service import DBService
import json


@web.middleware
async def json_check(request, handler):
    if request.method == 'POST':
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

        web.run_app(app, port=self._port)


class Handler:
    @staticmethod
    async def auth(request: web.Request):
        data = await request.json()

        if not all(key in data for key in ['login', 'password']):
            return web.json_response({'error_string': 'No login or password found'}, status=400)

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

        if not all(key in data for key in ['login', 'mail', 'password']):
            return web.json_response({'error_string': "Not enough arguments"}, status=400)

        login = data.get('login', None)
        mail = data.get('mail', None)
        password = data.get('password', None)

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
        data = request.query

        if not all(key in data for key in ['token', 'login']):
            return web.json_response({'error_string': 'No login found'}, status=400)

        token = data.get('token', None)
        login = data.get('login', None)

        db_service = DBService()

        user_data = db_service.get_profile(token=token, login=login)
        if user_data is not None:
            return web.json_response(user_data)
        return web.json_response({'error_string': "Wrong data or not enough data: must have 'login'"},
                                 status=400)

    @staticmethod
    async def logout(request: web.Request):
        data = await request.json()
        token = data.get('token', None)

        if token is None:
            return web.json_response({'error_string': 'No token found'}, status=400)

        db_service = DBService()
        if db_service.logout(token):
            return web.json_response()
        else:
            return web.json_response({'error_string': 'No token found'}, status=400)

    @staticmethod
    async def add_pokemon(request: web.Request):
        data = await request.json()

        if not all(key in data for key in ['token', 'name']):
            return web.json_response({"error_string': 'Not enough info. Must have 'token', 'name'"}, status=400)

        token = data.get('token', None)
        name = data.get('name', None)

        db_service = DBService()
        if db_service.add_pokemon(token, name):
            return web.json_response()
        return web.json_response({'error_string': 'Wrong data or pokemon exists'}, status=400)

    @staticmethod
    async def save_pokemon(request: web.Request):
        data = await request.json()
        if not all(key in data for key in ['token', 'name',
                                           'power', 'agility', 'loyalty',
                                           'satiety', 'health', 'max_health']):
            return web.json_response({'error_string': "Not enough info. Must have 'token', 'name',"
                                                      " 'power', 'agility', 'loyalty',"
                                                      " 'satiety', 'health', 'max_health'"}, status=400)

        db_service = DBService()
        if db_service.save_pokemon(data):
            return web.json_response()
        return web.json_response({'error_string': "Wrong data or not enough data: must have 'token', 'name', "
                                                  "'power', 'agility', 'loyalty', "
                                                  "'satiety', 'health', 'max_health'"}, status=400)

    @staticmethod
    async def get_pokemon(request: web.Request):
        data = request.query
        if not all(key in data for key in ['token', 'name']):
            return web.json_response({'error_string': 'No token or name found'}, status=400)

        db_service = DBService()
        token = data['token']
        name = data['name']

        pokemon_data = db_service.get_pokemon(token=token, name=name)
        if pokemon_data is not None:
            return web.json_response(pokemon_data)
        return web.json_response({'error_string': "Wrong data or not enough data: must have 'token', 'name'"},
                                 status=400)
