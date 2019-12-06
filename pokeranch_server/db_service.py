import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from pokeranch_server.models import User, Pokemon


class DBService:
    def __init__(self):
        cfg = Config("alembic.ini")

        engine = sa.create_engine(cfg.get_main_option('sqlalchemy.url'))
        self._session = sessionmaker(bind=engine)()

    def auth(self, login=None, mail=None, password=None):
        if login is not None:
            user_exists = self._session.query(User).filter_by(login=login, password=password).count()
            return bool(user_exists)
        if mail is not None:
            user_exists = self._session.query(User).filter_by(mail=mail, password=password).count()
            return bool(user_exists)
        return False

    def generate_token(self):
        pass

    def get_profile(self, login):
        pass

    def register_profile(self, login, mail, password):
        login_exists = self.has_user_by_login(login)
        mail_exists = self.has_user_by_mail(mail)

        if login_exists or mail_exists:
            return False
        else:
            new_user = User(login=login, mail=mail, password=password, pokemon_id=0)
            self._session.add(new_user)
            self._session.commit()
            return True

    def has_user_by_login(self, login):
        amount_of_users_with_login = self._session.query(User).filter_by(login=login).count()
        return bool(amount_of_users_with_login)

    def has_user_by_mail(self, mail):
        amount_of_users_with_mail = self._session.query(User).filter_by(mail=mail).count()
        return bool(amount_of_users_with_mail)

    def save_progress(self, **info):
        pass
