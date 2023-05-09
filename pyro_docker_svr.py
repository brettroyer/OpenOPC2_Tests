import Pyro5.api
from Pyro5.api import expose, Daemon
from docker.client import DockerClient

# expose the class from the library using @expose as wrapper function:
# DockerAdapterClass = Pyro5.api.expose(DockerClient)

# create adapter class that only exposes what should be accessible,
# and calls into the library class from there:


class DockerAdapterClass(DockerClient):
    @expose
    def from_env(self, **kwargs):
        print("Adapter class is called...")
        return super(DockerAdapterClass, self).from_env(**kwargs)


def main():
    with Daemon() as daemon:
        # register the adapter class instead of the library class itself:
        uri = daemon.register(DockerAdapterClass, "example.docker")
        print("adapter class registered, uri: ", uri)
        daemon.requestLoop()


if __name__ == '__main__':
    main()