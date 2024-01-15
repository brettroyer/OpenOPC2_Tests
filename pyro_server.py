import Pyro5
import Pyro5.server
import Pyro5.api
import Pyro5.core
import Pyro5.nameserver
import docker
import json


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class Warehouse(object):
    def __init__(self):
        self.contents = ["chair", "bike", "flashlight", "laptop", "couch"]

    def list_contents(self):
        return self.contents

    def take(self, name, item):
        self.contents.remove(item)
        print("{0} took the {1}.".format(name, item))

    def store(self, name, item):
        self.contents.append(item)
        print("{0} stored the {1}.".format(name, item))


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class pi4(object):

    def __int__(self):
        pass

    @property
    def client(self):
        return docker.from_env()

    def get_images(self):
        images = self.client.images.list()
        _images = [image.attrs['RepoTags'][0] for image in images]
        print(_images)
        return json.dumps(_images)

    def get_containers(self):
        containers = self.client.containers.list()
        _containers = [container.name for container in containers]
        print(_containers)
        return json.dumps(_containers)


def main_test(host, port):
    ns = Pyro5.core.locate_ns(host=host, port=int(port))
    daemon = Pyro5.server.Daemon()
    Pyro5.server.Daemon.serveSimple(
        {
            Warehouse: "example.warehouse",
            pi4: "docker"
        },
        ns=ns,
        daemon=daemon
    ),


def main(host, port):
    Pyro5.server.Daemon.serveSimple(
        {
            Warehouse: "example.warehouse",
            pi4: "docker"
        },
        ns=False,
        host=host,
        port=int(port)
    ),


if __name__ == '__main__':
    host = '192.168.1.50'
    port = '9050'
    # nameserverUri, nameserverDaemon, broadcastServer = Pyro5.nameserver.start_ns(host=host, port=int(port))
    # assert broadcastServer is not None, "expect a broadcast server to be created"
    # print("got a Nameserver, uri=%s" % nameserverUri)
    main(host, port)

