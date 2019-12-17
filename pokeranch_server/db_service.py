import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from pokeranch_server.models import User, Pokemon, Token
import secrets


class DBService:
    def __init__(self):
        cfg = Config("alembic.ini")

        engine = sa.create_engine(cfg.get_main_option('sqlalchemy.url'))
        self._session = sessionmaker(bind=engine)()

    def auth(self, login=None, mail=None, password=None):
        if login is not None:
            user = self._session.query(User).filter_by(login=login, password=password)
        elif mail is not None:
            user = self._session.query(User).filter_by(mail=mail, password=password)
        else:
            return None

        if user.count() == 0:
            return None

        user = user.first()
        return self.generate_token(user.id)

    def generate_token(self, user_id):
        token = secrets.token_urlsafe(20)

        while self._session.query(Token).filter_by(token=token).count():
            token = str(secrets.token_urlsafe(20))

        existing_token = self._session.query(Token).filter_by(user_id=user_id)
        if existing_token.count() == 1:
            new_token = existing_token.one()
            new_token.token = token
            self._session.commit()
            return token

        new_token = Token(user_id=user_id, token=token)
        self._session.add(new_token)
        self._session.commit()
        return token

    def create_user(self, login, mail, password):
        login_exists = self.has_user(login=login)
        mail_exists = self.has_user(mail=mail)

        if login_exists or mail_exists:
            return False
        else:
            new_user = User(login=login, mail=mail, password=password)
            self._session.add(new_user)
            self._session.commit()
            return True

    def get_profile(self, token, login):
        if self.get_user_id(token=token) is None:
            return None

        user = self._session.query(User).filter_by(login=login).first()
        if user is None:
            return None
        user_data = dict()
        user_data['id'] = user.id
        user_data['login'] = user.login

        pokemon = self._session.query(Pokemon).filter_by(owner_id=user.id).first()
        if pokemon is None:
            user_data['pokemon_name'] = None
            return user_data
        user_data['pokemon_name'] = pokemon.name
        return user_data

    def logout(self, token=None):
        has_token = self._session.query(Token).filter_by(token=token).count()
        if has_token:
            token = self._session.query(Token).filter_by(token=token).delete()
            self._session.commit()
            return True
        return False

    def has_user(self, login=None, mail=None):
        if login is not None:
            amount_of_users_with_login = self._session.query(User).filter_by(login=login).count()
            return bool(amount_of_users_with_login)
        if mail is not None:
            amount_of_users_with_mail = self._session.query(User).filter_by(mail=mail).count()
            return bool(amount_of_users_with_mail)

    def get_user_id(self, login=None, mail=None, pokemon_id=None, token=None):
        user = None

        if login is not None:
            user = self._session.query(User).filter_by(login=login).first()
        elif mail is not None:
            user = self._session.query(User).filter_by(mail=mail).first()
        elif pokemon_id is not None:
            user = self._session.query(Pokemon).filter_by(id=pokemon_id).first()
        elif token is not None:
            token_obj = self._session.query(Token).filter_by(token=token).first()
            if token_obj is not None:
                return token_obj.user_id
            else:
                return None

        if user is not None:
            return user.id
        else:
            return None

    def add_pokemon(self, token, name):
        user_id = self.get_user_id(token=token)

        has_pokemon = self._session.query(Pokemon).filter_by(owner_id=user_id).count()
        if has_pokemon:
            return False

        new_pokemon = Pokemon(owner_id=user_id, name=name)
        self._session.add(new_pokemon)
        self._session.commit()
        return True

    def save_pokemon(self, data: dict):
        token = data['token']
        name = data['name']

        user_id = self.get_user_id(token=token)
        pokemon = self._session.query(Pokemon).filter_by(owner_id=user_id, name=name).first()
        if pokemon is None:
            return False

        pokemon.agility = int(data['agility'])
        pokemon.loyalty = int(data['loyalty'])
        pokemon.satiety = int(data['satiety'])
        pokemon.health = int(data['health'])
        pokemon.max_health = int(data['max_health'])
        self._session.commit()
        return True

    def get_pokemon(self, token, name):
        user_id = self.get_user_id(token=token)
        pokemon = self._session.query(Pokemon).filter_by(owner_id=user_id).first()
        if pokemon is None:
            return None

        data = dict()
        data['name'] = name
        data['agility'] = pokemon.agility
        data['loyalty'] = pokemon.loyalty
        data['satiety'] = pokemon.satiety
        data['health'] = pokemon.health
        data['max_health'] = pokemon.max_health

        return data
