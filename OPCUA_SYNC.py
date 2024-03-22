import sys
import logging
from opcua import Client

logging.basicConfig(level=logging.WARN)


ip = '192.168.1.10'
port = '9409'
server = f"opc.tcp://{ip}:{port}/DvOpcUaServer"


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another 
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


def printChildren(children):
    for child in children:
        print(child)


def getChildren(Node, s='node'):
        children = Node.get_children()
        #print (f"{s.title()} children are: {children}")
        print (f"There are {len(children)} {s} children")
        print ("")
        return children


def browseModules(areas, client):
    for area in areas:
        tmp = client.get_node(area)
        print(tmp)


def getPathNames(cv, client):
    paths = cv.get_path()
    for path in paths:
        node = client.get_node(path)
        print(node.get_browse_name())
        print(node.get_display_name())


def getpath(node, client):
    """
    Print the Children of each node class
    return: List of Nodes (Children)
    """
    children = node.get_children()
    print (f"-----{node.get_browse_name()} Nodes: {len(children)} ------")
    print ("")
    for index, child in enumerate(children):
        node = client.get_node(child)
        print(f'{index} : {node.get_browse_name()}')
    print ('--------------------------------------------')
    return children


def listmodules(area, client):
    """
    : area should be a opcua Node class object
    """
    children = area.get_children()
    print (f"-----{area.get_browse_name()} Nodes: {len(children)} ------")
    print ("")
    for index, child in enumerate(children):
        node = client.get_node(child)
        print(f'{index} : {node.get_browse_name()}')
    print ('--------------------------------------------')
    return children


def main_old():
    client = Client("opc.tcp://192.168.1.10:9409/DvOpcUaServer")  # Connect to PA1 DeltaV OPC UA Server
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()
        client.load_type_definitions()  # load definition of server specific structures/extension objects

        # uri = 'opc.com://192.168.1.10/OPC.DeltaV.1/c3b72ab1-6b33-11d0-9007-0020afb6cf9f/DA'
        uri = client.get_namespace_array()[3]  # Only  NS=2 and NS=3 worked
        idx = client.get_namespace_index(uri)

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        # print("Root node is: ", root)
        # objects = client.get_objects_node()
        # print("Objects node is: ", objects)

        x1 = getpath(root, client) # Returns a list of root paths [0:Objects, 0:Types, 0:Views]
        x2 = getpath(x1[0], client)  # Returns a list of Objects paths [0:Server, 2:DA, 4:AE, 5:HDA]
        x3 = getpath(x2[1], client)  # Returns a list of DA paths [3:ServerStatus, 2:MODULES, 2:IO, 2:DIAGNOSTICS]
        x4 = getpath(x3[1], client)  # Returns the list of "Controls Strategies or Areas"
        x5 = listmodules(x4[22], client)  # Get list of modules in "REFORMER" area.
        x6 = listmodules(x5[76], client)  # Get Contents of "FIC1601"
        x7 = getpath(x6[25], client)  # Get PID1 Contents
        x8 = getpath(x7[113], client)  # Get PV of PID1
        tmp = x8[0]  # PV.CV
        path = tmp.get_path()
        value = tmp.get_value()

        """
        myvar = root.get_child(["0:Objects", 
                        "{}:DA".format(idx), 
                        "{}:MODULES".format(idx),
                        "{}:REFORMER".format(idx),
                        "{}:FIC1601".format(idx),
                        "{}:PID1".format(idx)
                        ])

        myvar = root.get_child(["0:Objects", 
                "{}:DA".format(idx), 
                "{}:FIC1601/PID1/PV.CV".format(idx)
                ])
        """

        pv = client.get_node(f"ns={idx};s=0:FIC1601/PID1/PV.CV")
        sp = client.get_node("ns=2;s=0:FIC1601/PID1/SP.CV")
        sp.get_value()

        out = client.get_node("ns=2;s=0:FIC1601/PID1/OUT.CV")
        out.get_value()

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        # print("Children of root are: ", root.get_children())

        # children = objects.get_children()
        # print(f"Children of Objects node are: {children}")

        # server = client.get_node(children[0]) # Get Node Class
        # s_children = getChildren(server, 'server')

        # da = client.get_node(children[1]) # Get Node Class
        # d_children = getChildren(da, 'DA')

        # areas = client.get_node(d_children[1])
        # a_children = getChildren(areas, 'area')

        # modules = client.get_node(a_children[22])  #Reformer Area
        # m_children = getChildren(modules, 'modules')   # m_children[75] = FIC1201

        # fb = m_children[75]
        # fb_children = getChildren(fb, 'function blocks')
        # [Node(StringNodeId(ns=2;s=0:FIC1201/LO_LIM.CV)), Node(StringNodeId(ns=2;s=0:FIC1201/LO_LIM.ST)), Node(StringNodeId(ns=2;s=0:FIC1201/LO_LIM.CST)), Node(StringNodeId(ns=2;s=0:FIC1201/LO_LIM.AWST))]

        # param = client.get_node(fb_children[50])
        # p_children = param.get_children()
        # cv = client.get_node(p_children[0])
        # cv.get_value()

        # cv.get_path() = [Node(TwoByteNodeId(i=84)), Node(TwoByteNodeId(i=85)), Node(StringNodeId(ns=2;s=0:)), Node(StringNodeId(ns=2;s=0:FIC1201)), Node(StringNodeId(ns=2;s=0:FIC1201/LO_LIM.CV))]
        # Now getting a variable node using its browse path
        # myvar = root.get_child(["0:Objects", "{}:MyObject".format(idx), "{}:MyVariable".format(idx)])
        # myvar = root.get_child(["0:Objects",
        # "{}:DA".format(idx),
        # "{}:MODULES".format(idx),
        # "{}:REFORMER".format(idx),
        # "{}:FI1051A".format(idx),
        # "{}:AI1".format(idx)
        # ])

        # browseModules(a_children)

        # printChildren(m_children)

        # get a specific node knowing its node id
        # var = client.get_node(ua.NodeId(1002, 2))
        # var = client.get_node("ns=2;i=13")
        # var = client.get_node("ns=2;g=1be5ba38-d004-46bd-aa3a-b5b87940c698")
        # print(var)
        # var.get_data_value() # get value of node as a DataValue object
        # var.get_value() # get value of node as a python builtin
        # var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        # var.set_value(3.9) # set node value using implicit data type

        # gettting our namespace idx
        # uri = "http://examples.freeopcua.github.io"
        # idx = client.get_namespace_index(uri)

        # Now getting a variable node using its browse path
        # myvar = root.get_child(["0:Objects", "{}:MyObject".format(idx), "{}:MyVariable".format(idx)])
        # obj = root.get_child(["0:Objects", "{}:MyObject".format(idx)])
        # print("myvar is: ", myvar)

        # subscribing to a variable node
        # handler = SubHandler()
        # sub = client.create_subscription(500, handler)
        # handle = sub.subscribe_data_change(myvar)
        # time.sleep(0.1)

        # we can also subscribe to events from server
        # sub.subscribe_events()
        # sub.unsubscribe(handle)
        # sub.delete()

        # calling a method on server
        # res = obj.call_method("{}:multiply".format(idx), 4, "klk")
        # print("method result is: ", res)
    finally:
        client.disconnect()


def get_client(svr):
    client = Client(server)
    client.description = "DeltaV OPCUA"

    try:
        client.connect()
        client.load_type_definitions()  # load definition of server specific structures/extension objects
        return client
    except:
        raise Exception()


def get_ns(client):
    # 'opc.com://PA1DEV01/OPC.DeltaV.1/c3b72ab1-6b33-11d0-9007-0020afb6cf9f/DA'
    uri = client.get_namespace_array()[2]  # Only  NS=2 and NS=3 worked
    logging.warning(uri)
    idx = client.get_namespace_index(uri)
    return idx


def main(svr):
    client = get_client(svr)
    ns = get_ns(client)

    # Get Multiple Values at one time.
    _nodes = [f"ns={ns};s=0:FIC1601/PID1/PV.CV",
              f"ns={ns};s=0:FIC1601/PID1/SP.CV",
              f"ns={ns};s=0:FIC1601/PID1/OUT.CV"]

    nodes = [client.get_node(node) for node in _nodes]  # Must create list of Node objects to pass to "get_values"
    logging.warning(client.get_values(nodes))

    # Get Individual Values.
    # logging.warning(client.get_node(f"ns={ns};s=0:FIC1601/PID1/PV.CV").get_value())
    # logging.warning(client.get_node(f"ns={ns};s=0:FIC1601/PID1/SP.CV").get_value())
    # logging.warning(client.get_node(f"ns={ns};s=0:FIC1601/PID1/OUT.CV").get_value())

    client.disconnect()


if __name__ == "__main__":
    main(server)

