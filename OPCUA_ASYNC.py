import asyncio
from asyncua import Client

ip = '192.168.1.10'
port = '9409'
server = f"opc.tcp://{ip}:{port}/DvOpcUaServer"
multiple = True


async def main1():
	client = Client(url=server, timeout=60)
	await client.connect()
	ns_array = await client.get_namespace_array()  # Only  NS=2 and NS=3 worked
	idx = await client.get_namespace_index(ns_array[2])

	if multiple:
		# Get Multiple Values at one time.
		_nodes = [f"ns={idx};s=0:FIC1601/PID1/PV.CV",
				  f"ns={idx};s=0:FIC1601/PID1/SP.CV",
				  f"ns={idx};s=0:FIC1601/PID1/OUT.CV"]

		nodes = [client.get_node(node) for node in _nodes]  # Must create list of Node objects to pass to "get_values"
		values = await client.get_values(nodes)
		print(values)
	else:
		# Get Individual Values.
		node = client.get_node(f"ns={idx};s=0:FIC1601/PID1/OUT.CV")
		value = await node.read_value()
		print(value)

	await client.disconnect()


async def main():
	async with Client(url=server, timeout=60) as client:
		ns_array = await client.get_namespace_array()  # Only  NS=2 and NS=3 worked
		idx = await client.get_namespace_index(ns_array[2])

		if multiple:
			# Get Multiple Values at one time.
			_nodes = [f"ns={idx};s=0:FIC1601/PID1/PV.CV",
					  f"ns={idx};s=0:FIC1601/PID1/SP.CV",
					  f"ns={idx};s=0:FIC1601/PID1/OUT.CV"]

			nodes = [client.get_node(node) for node in _nodes]  # Must create list of Node objects to pass to "get_values"
			values = await client.get_values(nodes)
			print(values)
		else:
			# Get Individual Values.
			node = client.get_node(f"ns={idx};s=0:FIC1601/PID1/OUT.CV")
			value = await node.read_value()
			print(value)


if __name__ == '__main__':
	asyncio.run(main1())
