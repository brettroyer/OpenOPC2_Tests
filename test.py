from openopc2.da_client import OpcDaClient
from openopc2.gateway_proxy import OpenOpcGatewayProxy
from openopc2.config import OpenOpcConfig

config = OpenOpcConfig()
config.OPC_SERVER = 'OPC.DeltaV.1'
config.OPC_HOST = "192.168.1.10"
# config.OPC_CLASS = "Graybox.OPC.DAWrapper"
config.OPC_CLASS = "OPC.Automation"
config.OPC_MODE = "gateway"
# opc = OpcDaClient(config)
opc = OpenOpcGatewayProxy(config.OPC_HOST, config.OPC_GATEWAY_PORT).get_opc_da_client_proxy()
server = OpenOpcGatewayProxy(config.OPC_HOST, config.OPC_GATEWAY_PORT).get_server_proxy()
opc.connect(config.OPC_SERVER, config.OPC_HOST)
opc.close()