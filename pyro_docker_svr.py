import Pyro5.api
from Pyro5.api import expose, Daemon
from docker.client import DockerClient

# from pyro_docker_serializer import *

# expose the class from the library using @expose as wrapper function:
# DockerAdapterClass = Pyro5.api.expose(DockerClient)

# create adapter class that only exposes what should be accessible,
# and calls into the library class from there:

class DockerAdapterClass(DockerClient):

    @expose
    def from_env(self, **kwargs):
        print("Adapter class is called...")
        return super(DockerAdapterClass, self).from_env(**kwargs)

    @expose
    def info(self, *args, **kwargs):
        return super(DockerAdapterClass, self).info(self, *args, **kwargs)


def main():

    with Daemon(host='192.168.1.50', port=8050) as daemon:
        # register the adapter class instead of the library class itself:
        uri = daemon.register(DockerAdapterClass, "remote.docker")
        print("adapter class registered, uri: ", uri)
        daemon.requestLoop()


if __name__ == '__main__':
    main()