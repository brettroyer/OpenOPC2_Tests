from Pyro5.api import Proxy
import Pyro5.errors

uri = input("Enter the URI of the thirdparty library object: ").strip()

with Proxy(uri) as remote:
    pass