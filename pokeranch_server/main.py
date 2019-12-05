from pokeranch_server.server_service import Server


def main():
    server = Server(8888)
    server.start()


if __name__ == '__main__':
    main()
