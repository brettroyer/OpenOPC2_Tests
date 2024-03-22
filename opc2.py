from openopc2.da_client import OpcDaClient, OPCError
from openopc2.gateway_proxy import OpenOpcGatewayProxy
from openopc2.config import OpenOpcConfig
from Pyro5.errors import ProtocolError
from app.signals import PySignals
import time
# import functools
from dataclasses import dataclass
from typing import Union, Type
from datetime import datetime
from app.options import optobj
from app.functions import ExecutionTime
from deprecated import deprecated
import json

from app.logger import setupLogger
logger = setupLogger(name='main.opc2logger')


@dataclass()
class opcTag(object):
    """
    OPC Tag Read from OpenOPC2
    """

    def __init__(self, v=None, error=None):
        self._v = v
        self.error = error


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
    Openopc2 Re-Class

    Base class for OpenOPC2 library.  will ether used 'OPCDAClient' or 'OpenOpcGatewayProxy'
    depending on if connecting via the 'gateway' option.
    https://github.com/iterativ/openopc2
    """

    signal = PySignals(name="OPC Signals")

    def __init__(self, options: Type[optobj],
                 connect: bool = False,
                 sleep: int = None,
                 counter: int = None):

        self.options = options

        if sleep is None:
            self.sleep = self.options.sleepTime  # Use default sleep time
        else:
            self.sleep = sleep  # use custom sleep time.
        self.counter = counter  # If none,  program will use len(inlist) in self.run()
        self.num_complete = 0  # Keep track of number complete to send back for progress bar
        self._connected = False
        self._opc = None
        self.server = None  # Sets currently connected server.

        if connect:
            self.connect()

    def __repr__(self):
        if self.options.connected:
            return "{} Connected".format(self.options.svr)
        return "{} Disconnected".format(self.options.svr)

    def __del__(self):
        logger.debug("Calling De-Constructor")
        self.close()

    def run(self, inlist: list):
        pass

    @property
    def server_name(self):
        return self.server

    @property
    def config(self) -> OpenOpcConfig:
        """
        OpenOPC2 class config requirement.

        Review config.py in the openopc2 directory.
        :return: OpenOpcConfig - Object containing all the configuration needed for OpenOPC2.
        """
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
                self._opc = OpenOpcGatewayProxy(self.config.OPC_GATEWAY_HOST,
                                                self.config.OPC_GATEWAY_PORT).get_opc_da_client_proxy()
                logger.info("Connecting in Gateway Mode")
            else:
                self._opc = OpcDaClient(self.config)
                logger.info("Connecting in COM Mode")

            self._opc.connect(self.config.OPC_SERVER, self.config.OPC_HOST)

        except ProtocolError as e:
            logger.info(f"ProtocalError: {e}")

        except OPCError as e:
            logger.info(f"OPCError: {e}")

        except Exception as e:
            logger.info(f"Unknown Connect Exception: {e}")

        else:
            self._connected = True
            self.options.opc_test_ok = True  # Update Global Options
            self.options.connected = True  # Update Global Options
            self.server = self.options.svr  # Sets currently connected server.

            logger.info(f"OPC Server Info: {self._opc.info()}")
            logger.info(f"Connected to {self.config.OPC_SERVER}")

    def close(self, delob: bool = True) -> None:
        if self.connected:
            logger.info(f"Closing Connection to {self.config.OPC_SERVER}")
            for x in range(2):
                try:
                    self.opc.close(del_object=delob)
                    self._connected = False
                    self.options.connected = False  # Update Global Options
                    self.options.opc_test_ok = False  # Update Global Options
                    self.server = None
                    logger.info(f"Connection Closed to {self.config.OPC_SERVER}")
                except Exception as e:
                    logger.debug(f"Unknown Close Exception: {e}")

    def restart(self):
        pass

    @deprecated
    def _read(self, taglist: list):
        """ Read OPC from Server. OLD READ FUNCTION"""

        @dataclass()
        class data(object):

            def __repr__(self):
                return str(self.v)

            def __str__(self):
                return str(self.v)

            v = None
            status = "not connected"
            error = None

        if self.options.connected:

            if isinstance(taglist, list):
                """ For reading list of tags """
                try:
                    timer = ExecutionTime()  # Start the timer
                    data.v = self.opc.read(tags=taglist, timeout=self.options.timeout)
                    # TODO: Add options to read function.  Explore the use of size, group, rebuild, etc.
                    logger.info('Finished read in {} seconds.'.format(timer.duration()))
                    data.status = "good"
                except TimeoutError as e:
                    data.error = e
                    data.status = "timeout"
                    logger.info('OPC TimeoutError')
                except Exception as e:
                    data.error = e
                    data.status = "bad"
                    logger.debug('Some assigned modules may be disconnected')
                    logger.debug('OPC Tag Read Error: {}'.format(e))
            elif isinstance(taglist, str):
                """ For reading single instance """
                try:
                    data.v = self.opc.read(taglist, timeout=self.options.timeout)
                    data.status = "good"
                except TimeoutError as e:
                    data.error = e
                    data.status = "timeout"
                    logger.info('OPC TimeoutError')
                except Exception as e:
                    data.error = e
                    data.status = "bad"
                    logger.debug('Some assigned modules may be disconnected')
                    logger.debug('OPC Tag Read Error: {}'.format(e))
            else:
                # TODO: Provide for better error.
                data.status = "taglist should be list or string"
                logger.debug("taglist should be list or string")

        return data

    def read(self, readdata: Union[list, str], sync: bool = False) -> dataclass():

        _v = None
        _error = None

        if self.connected:
            """ For reading single or list instance """
            try:
                _v = self.opc.read(tags=readdata,
                                   group='DVUTIL',
                                   size=self.options.sliceamt,  # Slice Amount
                                   pause=self.sleep * 1000,  # In between size reads
                                   timeout=self.options.timeout,
                                   include_error=True,
                                   rebuild=False,
                                   sync=sync)
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

    def read_null(self):
        """
        Set OPC Read Count to 0.
        This didn't fix the issue of not disconnecting from DeltaV.
        """
        logger.info("Setting OPC Read Count to 0")
        null = self.opc.read()

    def write_single(self, tag, value):
        self.opc.write((tag, value))

    def write(self, tags):
        self.opc.write(tags)

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

    def __init__(self, options: Type[optobj], connect: bool = True, sleep: int = None, counter: int = None):
        super().__init__(options, connect, sleep, counter)

    def run(self, inlist: list):
        timer = ExecutionTime()  # Start the timer
        if self.counter is None:
            self.options.counter = len(inlist)  # For progressbar (Default)
        else:
            self.options.counter = self.counter  # For progressbar (Custom)

        self.signal.progress(self.num_complete)  # Should send a 0 to the progress bar
        x = self.read(inlist)
        x = [self.results(list(ele)) for ele in x._v]
        # x = self.read_slices(inlist)
        logger.info(' #### Finished Overall Read in {} minutes.'.format(timer.duration()/60))
        return x

    @deprecated
    def read_slices(self, inlist: list) -> list:
        """
                Read OPC Main Loop.

                Note:  Main function call is to self.run
                :param inlist - list of strings to read via OPC
                :return List
                """

        class maindata():
            retry = False
            count = 0  # Retry Count
            return_list = []
            start = 0  # lowest list element

        if self.options.connected:
            while maindata.start <= len(inlist):
                end = maindata.start + self.options.sliceamt  # Control the number of OPC Reads at a time.
                if end > len(inlist):
                    end = len(inlist)  # If the last slice is greater than the amount left,  choose the lower number.

                if maindata.retry:
                    msg = 'retrying {} to {} out of {}'.format(maindata.start, end, len(inlist))
                else:
                    msg = 'reading {} to {} out of {}'.format(maindata.start, end, len(inlist))

                logger.info(msg)
                self.signal.msg(msg)

                # Loading Tag Group for OPC Read.
                # TODO: Create Group to see if larger read slices can be made
                taglist = [line.strip() for line in inlist[maindata.start:end]]

                data = self._read(taglist)  # Read OPC Data
                # TODO:  Add option to disconnect/close connection after every read.
                if data.status == 'good':
                    # TODO: Send progress update
                    self.num_complete += len(taglist)
                    self.signal.progress(self.num_complete)  # Send how many of the inlist has been read
                    maindata.retry = False
                    maindata.count = 0
                    maindata.start = maindata.start + self.options.sliceamt  # list starts with index 0 (ie:  with a slice of 500, the first read would be 0-499)
                    maindata.return_list.extend(self.results(data.v))
                    logger.info('Sleeping for {} seconds'.format(self.options.sleepTime))
                    time.sleep(self.sleep)
                elif data.status == 'bad':
                    logger.info(data.error)
                    break
                elif data.status == 'timeout':
                    maindata.count += 1
                    if maindata.count > self.options.retry_count:
                        msg = 'OPC Read Failed after {} attempts'.format(self.options.retry_count)
                        logger.debug(msg)
                        self.signal.msg(msg)
                        break

                    self.restart()  # Attempt to reconnect to OPC server.

                    logger.debug('Retry #{}'.format(maindata.count))
                    maindata.retry = True
                    logger.debug("Multiplier: {}".format(self.options.pct_num))
                    self.options.sliceamt = int(self.options.sliceamt - self.options.sliceamt * .20)

        return maindata.return_list

    @deprecated
    def results(self, v):
        """
        Write OPC Data to list.

        :var v - Input from opc read.
        :return List
        """
        tmp = []
        for i in range(len(v)):
            try:
                (name, val, qual, time_stamp) = v[i]
                tmp.append('{},{},{}'.format(name, str(val), qual))
            except ValueError as e:
                # Split into comma separated string.
                # TODO:  May require further investigation on possible results.  This worked for RSLinx OPC.
                (name, val, qual) = v[i].split(',')
                tmp.append('{},{},{}'.format(name, str(val), qual))
        return tmp


def main():
    pass


if __name__ == '__main__':
    main()
