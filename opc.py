from openopc2.da_client import OpcDaClient, OPCError
from openopc2.gateway_proxy import OpenOpcGatewayProxy
from openopc2.config import OpenOpcConfig
from Pyro5.errors import ProtocolError
from signals import PySignals
import time
import functools
from dataclasses import dataclass
from typing import Union, Type
from datetime import datetime
from options import optobj
import json

from logger import setupLogger
logger = setupLogger(name='main.opclogger')


@dataclass()
class opcData(object):
    """
    Dataclass for storing data read via OPC
    """

    def __init__(self, v=None, error=None):
        self._v = v
        self.error = error

    def __repr__(self):
        return str(self._v)

    def __str__(self):
        return str(self._v)

    @property
    def type(self):
        if isinstance(self._v, tuple):
            return "single"
        elif isinstance(self._v, list):
            return "multiple"

    @property
    def isMultiple(self):
        if isinstance(self._v, list):
            return True
        return False

    @property
    def value(self):
        if isinstance(self._v, tuple):
            return self._v[0]
        elif isinstance(self._v, list):
            # values = [value[1] for value in self._v]
            return None

    @property
    def status(self):
        if isinstance(self._v, tuple):
            return self._v[1]
        elif isinstance(self._v, list):
            # status = [value[2] for value in self._v]
            return None

    @property
    def timestamp(self):
        if isinstance(self._v, tuple):
            return datetime.fromisoformat(self._v[2])
        elif isinstance(self._v, list):
            # timestamps = [value[3] for value in self._v]
            return None


class OpcBase(object):
    """
    Base class for OpenOPC2 library.  will ether used 'OPCDAClient' or 'OpenOpcGatewayProxy'
    depending on if connecting via the 'gateway' option.
    https://github.com/iterativ/openopc2
    """

    signal = PySignals(name="OPC Signals")

    def __init__(self, options: Type[optobj], connect: bool = False):
        self.options = options
        self.config = self._config()
        self._connected = False
        self._opc = None

        if connect:
            self.connect()

    def __del__(self):
        logger.debug("Calling De-Constructor")
        self.close()

    def _config(self) -> OpenOpcConfig:
        config = OpenOpcConfig()
        # config.OPC_SERVER = "OPC.DeltaV.1" if self.svr is None else self.svr
        config.OPC_SERVER = "Matrikon.OPC.Simulation" if self.options.svr is None else self.options.svr
        config.OPC_GATEWAY_HOST = "192.168.1.10" if self.options.ip is None else self.options.ip
        config.OPC_CLASS = "Graybox.OPC.DAWrapper"
        config.OPC_MODE = self.options.mode
        return config

    @property
    def opc(self):
        return self._opc

    @property
    def connected(self):
        return self._connected

    def connect(self) -> None:
        logger.info(f'Attempting Connection to {self.config.OPC_SERVER}')
        try:
            if self.config.OPC_MODE == "gateway":
                self._opc = OpenOpcGatewayProxy(self.config.OPC_GATEWAY_HOST, self.config.OPC_GATEWAY_PORT).get_opc_da_client_proxy()
                logger.info("Connecting in Gateway Mode")
            else:
                self._opc = OpcDaClient(self.config)
                # self._opc.set_trace(True)
                logger.info("Connecting in COM Mode")

            self._opc.connect(self.config.OPC_SERVER, self.config.OPC_HOST)
            self._connected = True
            logger.info(self._opc.info())
            logger.info(f"Connected to {self.config.OPC_SERVER}")

        except ProtocolError as e:
            logger.debug(e)

        except OPCError as e:
            logger.debug(e)

        except Exception as e:
            logger.debug(f"Unknown Connect Exception: {e}")

    def close(self, delob: bool = True) -> None:
        if self.connected:
            logger.info(f"Closing Connection to {self.config.OPC_SERVER}")
            for x in range(2):
                try:
                    self.opc.close(del_object=delob)
                    self._connected = False
                except Exception as e:
                    logger.debug(f"Unknown Close Exception: {e}")

            logger.info(f"Connection Closed to {self.config.OPC_SERVER}")

    def read(self, readdata: Union[list, str], sync: bool = False) -> dataclass():

        _v = None
        _error = None

        if self.connected:
            """ For reading single or list instance """
            try:
                _v = self.opc.read(readdata, timeout=self.options.timeout, sync=sync)
            except TimeoutError as e:
                _error = e
                logger.debug(f'OPC TimeoutError: {e}')
            except OPCError as e:
                _error = e
                logger.debug(f'OPC Tag Read Error: {e}')
            except Exception as e:
                _error = e
                logger.debug(f'Read Unknown Exception: {e}')

        data = opcData(_v, _error)
        return data

    def write_to_json(self, infile: str, data):
        logger.info('Writing File to {}'.format(infile))
        with open(infile, 'w') as fp:
            json.dump(data, fp)

    def read_from_json(self, json_file: str) -> dict:
        logger.info('Reading {} from file'.format(json_file))
        with open(json_file, 'r') as fp:
            return json.load(fp)

    @staticmethod
    def list_to_file(inlist, outfile):
        """
        File created from input list.
        :param. inlist = python list to be written to file
        :return None"""

        if outfile != '':
            filecount = 0
            filenm = outfile[:(outfile.rfind("."))]
            fileext = outfile[(outfile.rfind(".")):]

            try:
                out_file = open(outfile, 'w')
            except IOError:
                filecount += 1
                out_file = ''.join([filenm, str(filecount), fileext])

            for line in inlist:
                out_file.write('{}\n'.format(line.strip()))
            out_file.close()

    @staticmethod
    def list_from_file(filename: str) -> list:
        """
        Create python list from .txt file.

        :param filename = filename.txt or other text input
        :return List = Python List of filename content
         """
        with open(filename, 'r', encoding='utf-8', errors='ignore') as In_File:
            # x = []
            # for line in In_File:
            #     x.append(line.strip().rstrip())
            #
            x = [line.strip().rstrip() for line in In_File]
        return x


class Opc(OpcBase):

    def __init__(self, options: Type[optobj], connect: bool = True):
        super().__init__(options, connect)
        pass


class OpcTest(OpcBase):

    def __init__(self, options: Type[optobj], connect: bool = True):
        super().__init__(options, connect)
        self.paths = "*"
        self.limit = False
        self.n_reads = 1
        self.sync = False
        self.read = False

    def run(self):
        tags = self.list_from_file('tags.txt')
        self.read = True
        self.read_tags(tags, 'Simulation')
        self.close()

    @functools.cached_property
    def tags(self):
        """
        Return flat list of tags form the OPC Simulator

        :return:
        """
        tags = self.opc.list(paths=self.paths, recursive=False, include_type=False, flat=True)
        return [tag for tag in tags if "@" not in tag]

    @functools.cached_property
    def info(self):
        return self.opc.info()

    def main(self):
        logger.info(self.read("FIC1601/PID1/PV.CV"))

        # if limit:
        #     tags = tags[:limit]
        # logger.info("TAGS:")
        # for n, tag in enumerate(tags):
        #     logger.info(f"{n:3} {tag}")

        # logger.info("READ:")
        # for n, tag in enumerate(self.tags):
        #     start = time.time()
        #     read = self.read(tag, sync=self.sync)
        #     logger.info(f'{n:3} {time.time() - start:.3f}s {tag} {read}')

        # logger.info("READ: LIST")
        # for n in range(self.n_reads):
        #     start = time.time()
        #     read = self.read(self.tags, sync=self.sync)
        #     logger.info(f'{n:3} {time.time() - start:.3f}s {read}')

        # logger.info("PROPERTIES:")
        # for n, tag in enumerate(tags):
        #     start = time.time()
        #     properties = client.properties(tag)
        #     logger.info(f'{n:3} {time.time() - start:.3f}s {tag} {properties}')

        # logger.info("PROPERTIES LIST:")
        # for n in range(self.n_reads):
        #     start = time.time()
        #     properties = self.opc.properties(self.tags)
        #     logger.info(f'{n} {time.time() - start:.3f}s {properties}')

    def read_tags(self, tags: list, group: str = 'Dummy'):
        """
        example point: tuple (tagname, data*, status, timestamp)
        TODO: type check data.
        :param tags: list of tags to scan
        :param group: Groupname for tags.
        :return: None
        """

        while self.read:
            data = self.opc.read(tags, group=group)
            points = []
            for point in data:
                points.append({
                    "measurement": "data",  # Group
                    "tags": {"location": "Port Neches"},  # "path": opc path
                    "fields": {point[0]: point[1]}, # Tagname : Data
                    "time": point[3]  # OPC Time Field
                })

            time.sleep(2)


    def write_tags(self):
        pass


def main():
    options = optobj
    # options.svr = 'OPC.DeltaV.1'
    options.svr = 'Matrikon.OPC.Simulation.1'
    options.ip = '192.168.1.2'
    options.mode = 'gateway'  # TODO: Update Main Options with new parameter mode,  remove local
    options.sleepTime = 1
    options.timeout = 5000 * 4
    options.sliceamt = 1000
    # TODO: Add sleep and counter to OPC Class parameters.
    opc = OpcTest(options)
    opc.run()


if __name__ == '__main__':
    main()
