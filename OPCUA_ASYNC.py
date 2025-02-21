import asyncio
from asyncua import Client

ip = '192.168.1.10'
port = '9409'
server = f"opc.tcp://{ip}:{port}/DvOpcUaServer"
multiple = True


class SubHandler(object):
    def datachange_notification(self, node, val, data):
        print("New data change ", node, val)


def parse_blockerr_data(data: int):
    """
	Parse DeltaV's BLOCK_ERR into usable errors.

	 BLOCK_ERROR = 16 bits (15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0)
	 bit#0 - Out Of Service
	 bit#1 - Power Up
	 bit#2 - Device Needs Maintenance Now
	 bit#3 - Readback Failed
	 bit#4 - Lost Non-Volatile Data
	 bit#5 - Lost Status Data
	 bit#6 - Memory Failure
	 bit#7 - Output Failure
	 bit#8 - Input Failure/Bad PV
	 bit#9 - Device Needs Maintenance Soon
	 bit#10 - Device Fault State Set
	 bit#11 - Local Overide
	 bit#12 - Simulate Active
	 bit#13 - Link Configuration Error
	 bit#14 - Configuration Error
	 bit#15 - Other Error

	:data: int - int representing the Block Error code
	"""
    _dict = {
        0: 'Out Of Service',
        1: 'Power Up',
        2: 'Device Needs Maintenance Now',
        3: 'Readback Failed',
        4: 'Lost Non-Volatile Data',
        5: 'Lost Status Data',
        6: 'Memory Failure',
        7: 'Output Failure',
        8: 'Input Failure/Bad PV',
        9: 'Device Needs Maintenance Soon',
        10: 'Device Fault State Set',
        11: 'Local Overide',
        12: 'Simulate Active',
        13: 'Link Configuration Error',
        14: 'Configuration Error',
        15: 'Other Error',
    }
    integer = int(float(data))
    _x = format(int(integer), '016b')  # Will produce a 0000000000000000 - 16 bits
    x = list(reversed([int(y) for y in _x]))  # Convert them to a list.  Reverse 15-0 bits to 0-15 bits.

    # For each dictionary item,  match 16-bit list with item. append only active bits.
    active = [v for k, v in _dict.items() if x[k]]
    print(active)


async def main1():
    client = Client(url=server, timeout=60)
    client.session_timeout = 600000
    await client.connect()
    ns_array = await client.get_namespace_array()  # Only  NS=2 and NS=3 worked
    idx = await client.get_namespace_index(ns_array[2])

    if multiple:
        # Get Multiple Values at one time.
        _nodes = [f"ns={idx};s=0:FIC1601/PID1/PV.CV",  # 0
                  f"ns={idx};s=0:FIC1601/PID1/SP.CV",  # 1
                  f"ns={idx};s=0:FIC1601/PID1/OUT.CV",  # 2
                  f"ns={idx}; s=0:FIC1601/AO1/BLOCK_ERR.CV"]  # 3

        nodes = [client.get_node(node) for node in _nodes]  # Must create list of Node objects to pass to "get_values"
        values = await client.get_values(nodes)
        print(values)
        parse_blockerr_data(values[3])
    else:
        # Get Individual Values.
        node = client.get_node(f"ns={idx};s=0:FIC1601/PID1/OUT.CV")
        value = await node.read_value()
        print(value)

    await client.disconnect()


async def main3():
    client = Client(url=server, timeout=60)
    client.session_timeout = 600000
    await client.connect()
    ns_array = await client.get_namespace_array()  # Only  NS=2 and NS=3 worked
    idx = await client.get_namespace_index(ns_array[2])
    myvar = client.get_node(f"ns={idx};s=0:FIC1601/PID1/PV.CV")
    handler = SubHandler()
    sub = await client.create_subscription(500, handler)
    handle = await sub.subscribe_data_change(myvar)


async def main():
    async with Client(url=server, timeout=60) as client:
        ns_array = await client.get_namespace_array()  # Only  NS=2 and NS=3 worked
        idx = await client.get_namespace_index(ns_array[2])

        if multiple:
            # Get Multiple Values at one time.
            _nodes = [f"ns={idx};s=0:FIC1601/PID1/PV.CV",
                      f"ns={idx};s=0:FIC1601/PID1/SP.CV",
                      f"ns={idx};s=0:FIC1601/PID1/OUT.CV"]

            nodes = [client.get_node(node) for node in
                     _nodes]  # Must create list of Node objects to pass to "get_values"
            values = await client.get_values(nodes)
            print(values)
        else:
            # Get Individual Values.
            node = client.get_node(f"ns={idx};s=0:FIC1601/PID1/OUT.CV")
            value = await node.read_value()
            print(value)


if __name__ == '__main__':
    asyncio.run(main1())
