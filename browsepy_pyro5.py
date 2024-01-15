from Pyro5.api import Proxy
import Pyro5.client
import json

# from pyro_docker_serializer import *


# uri = 'PYRO:browsepy.info@192.168.1.2:8050'
# info = Pyro5.client.Proxy(uri)


class RemoteClient(object):
    """
    Remote Extention to Docker library.
    Requires Pyro5 Server
    """

    def __init__(self, host, port):
        self.uri = f"PYRO:{'browsepy.info'}@{host}:{port}"
        self._info = Pyro5.client.Proxy(self.uri)

    def test(self):
        return self._info.test()


def connect():
    host = '192.168.1.2'
    port = '8050'
    info = RemoteClient(host, port)
    print(info.test())


if __name__ == '__main__':
    pass
    # with Proxy(uri) as info:
    #     client = info.getUserByToken()
    #     client.images.list()