from setuptools import setup, find_packages

setup(
    name='PokeRanchPythonServer',
    version='0.1',
    description="Server for PokeRanch game",
    license='BSD3',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'SQLAlchemy',
        'alembic'
    ],
    entry_points={
        'console_scripts': ['pokeranch_server=pokeranch_server.main:main'],
    },
)
