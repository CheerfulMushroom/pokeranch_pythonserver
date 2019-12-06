from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = sa.Column('id', sa.Integer(), nullable=False, unique=True, primary_key=True)
    login = sa.Column('login', sa.String(50), nullable=False, unique=True)
    mail = sa.Column('mail', sa.String(50), nullable=False, unique=True)
    password = sa.Column('password', sa.String(50), nullable=False)
    pokemon_id = sa.Column('pokemon_id', sa.Integer(), nullable=False, unique=True)

    def __repr__(self):
        return f"Login: {self.login}; PokID: {self.pokemon_id}"


class Pokemon(Base):
    __tablename__ = 'pokemons'

    id = sa.Column('id', sa.Integer(), nullable=False, unique=True, primary_key=True)
    name = sa.Column('name', sa.String(50), nullable=False)
    power = sa.Column('power', sa.Integer, nullable=False)
    agility = sa.Column('agility', sa.Integer(), nullable=False)
    loyalty = sa.Column('loyalty', sa.Integer(), nullable=False)
    satiety = sa.Column('satiety', sa.Integer(), nullable=False)
    health = sa.Column('health', sa.Integer(), nullable=False)
    max_health = sa.Column('max_health', sa.Integer(), nullable=False)

    def __repr__(self):
        return f'PokID: {self.id}; Name: {self.name}'
