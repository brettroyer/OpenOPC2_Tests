import Pyro5.client
import json


class Person(object):
    def __init__(self, name):
        self.name = name

    def visit(self, warehouse):
        print("This is {0}.".format(self.name))
        self.deposit(warehouse)
        self.retrieve(warehouse)
        print("Thank you, come again!")

    def deposit(self, warehouse):
        print("The warehouse contains:", warehouse.list_contents())
        item = input("Type a thing you want to store (or empty): ").strip()
        if item:
            warehouse.store(self.name, item)

    def retrieve(self, warehouse):
        print("The warehouse contains:", warehouse.list_contents())
        item = input("Type something you want to take (or empty): ").strip()
        if item:
            warehouse.take(self.name, item)


class RemoteDocker(object):
    """
    Remote Extention to Docker library.
    Requires Pyro5 Server
    """

    def __init__(self, host, port):
        self.uri = f"PYRO:{'docker'}@{host}:{port}"
        self._docker = Pyro5.client.Proxy(self.uri)

    def images(self):
        return json.loads(self._docker.get_images())

    def containers(self):
        return json.loads(self._docker.get_containers())


def warehouse_main():

    # uri = input("Enter the uri of the warehouse: ").strip()
    ns1 = 'example.warehouse'
    host= '192.168.1.50'
    port= '9050'
    uri = f"PYRO:{ns1}@{host}:{port}"
    warehouse = Pyro5.client.Proxy(uri)
    janet = Person("Janet")
    henry = Person("Henry")
    janet.visit(warehouse)
    henry.visit(warehouse)


def main():
    host= '192.168.1.50'
    port= '9050'
    docker = RemoteDocker(host, port)
    print(docker.images())
    print(docker.containers())


if __name__ == '__main__':
    main()