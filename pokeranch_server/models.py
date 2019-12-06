from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = sa.Column('id', sa.Integer(), nullable=False, unique=True, primary_key=True, autoincrement=True)
    login = sa.Column('login', sa.String(50), nullable=False, unique=True)
    mail = sa.Column('mail', sa.String(50), nullable=False, unique=True)
    password = sa.Column('password', sa.String(50), nullable=False)

    def __repr__(self):
        return f"Login: {self.login}; ID: {self.id}"


class Pokemon(Base):
    __tablename__ = 'pokemons'

    id = sa.Column('id', sa.Integer(), nullable=False, unique=True, primary_key=True, autoincrement=True)
    owner_id = sa.Column('owner_id', sa.Integer(), nullable=False)
    name = sa.Column('name', sa.String(50), nullable=False)
    power = sa.Column('power', sa.Integer, nullable=False)
    agility = sa.Column('agility', sa.Integer(), nullable=False)
    loyalty = sa.Column('loyalty', sa.Integer(), nullable=False)
    satiety = sa.Column('satiety', sa.Integer(), nullable=False)
    health = sa.Column('health', sa.Integer(), nullable=False)
    max_health = sa.Column('max_health', sa.Integer(), nullable=False)

    def __repr__(self):
        return f'PokName: {self.name}; PokID: {self.id}'


class Token(Base):
    __tablename__ = 'tokens'

    user_id = sa.Column('user_id', sa.Integer(), nullable=False, unique=True, primary_key=True)
    token = sa.Column('token', sa.String(20), nullable=False, unique=True)

    def __repr__(self):
        return f'UID: {self.user_id}; Token: {self.token[:8]}'
