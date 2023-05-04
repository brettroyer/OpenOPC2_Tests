from openopc2.da_client import OpcDaClient
from openopc2.config import OpenOpcConfig

config = OpenOpcConfig()
config.OPC_SERVER = "Matrikon.OPC.Simulation"
config.OPC_GATEWAY_HOST = "192.168.0.115"
config.OPC_CLASS = "Graybox.OPC.DAWrapper"
config.OPC_MODE = "com"
opc = OpcDaClient(config)
opc.connect(config.OPC_SERVER, config.OPC_HOST)
opc.close()