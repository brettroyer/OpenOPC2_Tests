from Pyro5.api import Proxy

# from pyro_docker_serializer import *


uri = 'PYRO:remote.docker@192.168.1.50:8050'


if __name__ == '__main__':
    with Proxy(uri) as remote:
        client = remote.from_env()
        client.images.list()