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
async def auth_check(request, handler):
    if request.method not in ['POST', 'GET']:
        return await handler(request)

    data = dict()
    if request.method == 'POST':
        data = await request.json()
    elif request.method == 'GET':
        data = request.query

    if 'token' in data:
        token = data['token']

        db_service = DBService()
        if not db_service.profile_is_authorized(token=token):
            return web.json_response({'error_string': f"Invalid token, not authorized"}, status=401)

    return await handler(request)


@web.middleware
async def log_host(request, handler):
    addr = request.host
    print(f"Connected: {request.rel_url}")
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
        app = web.Application(middlewares=[log_host, json_check, auth_check])
        app.router.add_route('POST', '/auth', Handler.auth)
        app.router.add_route('POST', '/register', Handler.register)
        app.router.add_route('GET', '/get_profile', Handler.get_profile)
        app.router.add_route('POST', '/logout', Handler.logout)

        app.router.add_route('POST', '/save_trainer', Handler.save_trainer)
        app.router.add_route('GET', '/get_trainer', Handler.get_trainer)

        app.router.add_route('POST', '/save_pokemon', Handler.save_pokemon)
        app.router.add_route('GET', '/get_pokemon', Handler.get_pokemon)

        web.run_app(app, port=self._port, reuse_port=True, reuse_address=True)


class Handler:
    @staticmethod
    async def auth(request: web.Request):
        data = await request.json()

        requirements = ['login', 'password']
        if not all(key in data for key in requirements):
            return web.json_response({"error_string": f"Not enough info. Must have {requirements}"}, status=400)

        login = data['login']
        password = data['password']

        db_service = DBService()
        if '@' in login:
            token = db_service.auth(mail=login, password=password)
        else:
            token = db_service.auth(login=login, password=password)

        if token is None:
            return web.json_response({'error_string': f"User not found"}, status=404)

        return web.json_response({'token': token})

    @staticmethod
    async def register(request: web.Request):
        data = await request.json()

        requirements = ['login', 'mail', 'password']
        if not all(key in data for key in requirements):
            return web.json_response({"error_string": f"Not enough info. Must have {requirements}"}, status=400)

        login = data.get('login', None)
        mail = data.get('mail', None)
        password = data.get('password', None)

        if '@' not in mail:
            return web.json_response({'error_string': "Mail doesn't have '@' in it"}, status=400)

        if '@' in login:
            return web.json_response({'error_string': "Login has '@' in it"}, status=400)

        db_service = DBService()
        if db_service.add_profile(login=login, mail=mail, password=password):
            return web.json_response({})
        return web.json_response({'error_string': "User with such login or mail already exists"}, status=400)

    @staticmethod
    async def get_profile(request: web.Request):
        data = request.query

        requirements = ['token', 'login']
        if not all(key in data for key in requirements):
            return web.json_response({"error_string": f"Not enough info. Must have {requirements}"}, status=400)

        token = data['token']
        login = data['login']

        db_service = DBService()

        user_data = db_service.get_profile(token=token, login=login)
        if user_data is not None:
            return web.json_response(user_data)
        return web.json_response({'error_string': f"Not found"}, status=404)

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

    # TRAINERS

    @staticmethod
    async def save_trainer(request: web.Request):
        data = await request.json()

        requirements = ['token', 'name']
        if not all(key in data for key in requirements):
            return web.json_response({'error_string': f"Not enough info. Must have {requirements}"}, status=400)

        db_service = DBService()
        if db_service.save_trainer(data):
            return web.json_response()
        return web.json_response({'error_string': f"Not found"}, status=404)

    @staticmethod
    async def get_trainer(request: web.Request):
        data = request.query

        requirements = ['token']
        if not all(key in data for key in requirements):
            return web.json_response({'error_string': f"Not enough info. Must have {requirements}"}, status=400)

        db_service = DBService()
        token = data['token']

        trainer_data = db_service.get_trainer(token=token)
        if trainer_data is not None:
            return web.json_response(trainer_data)
        return web.json_response({'error_string': f"Not found"}, status=404)

    # POKEMONS

    @staticmethod
    async def save_pokemon(request: web.Request):
        data = await request.json()
        requirements = ['token', 'name', 'power', 'agility', 'loyalty', 'satiety', 'health', 'max_health']

        if not all(key in data for key in requirements):
            return web.json_response({'error_string': f"Not enough info. Must have {requirements}"}, status=400)

        db_service = DBService()
        if db_service.save_pokemon(data):
            return web.json_response()
        return web.json_response({'error_string': f"Not found"}, status=404)

    @staticmethod
    async def get_pokemon(request: web.Request):
        data = request.query

        requirements = ['token']
        if not all(key in data for key in requirements):
            return web.json_response({'error_string': f"Not enough info. Must have {requirements}"}, status=400)

        db_service = DBService()
        token = data['token']

        pokemon_data = db_service.get_pokemon(token=token)
        if pokemon_data is not None:
            return web.json_response(pokemon_data)
        return web.json_response({'error_string': f"Not found"}, status=404)
