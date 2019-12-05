from setuptools import setup, find_packages

setup(
    name='PokeRanchServer',
    version='0.1',
    description="Server for PokeRanch game",
    license='BSD3',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': ['pokeranch_server=pokeranch_server.main:main'],
    },
)
