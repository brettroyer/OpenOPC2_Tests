import logging
# from concurrent_log_handler import ConcurrentRotatingFileHandler
import os
import sys


def setupLogger(name='logger', filename='logger', level=logging.DEBUG):
    # Basic Guide : https://www.loggly.com/ultimate-guide/python-logging-basics/
    # help: https://docs.python.org/3/library/logging.html  # logging.Formatter.format
    # https://github.com/Preston-Landers/concurrent-log-handler

    # TODO: if debugging is set to true,  set level to DEBUG else set to WARNING (Lowest Level).
    #  issues is that the options are not known.

    logger = logging.getLogger(name)
    logger.setLevel(level)  # Set the base level
    logger.propagate = False
    maxKB = 1000  # Max Size of log file.
    logfile = f"{os.getcwd()}/{filename}.log"

    if not logger.handlers:
        sh = logging.StreamHandler()
        shformat = logging.Formatter('%(levelname)s - %(filename)s - %(message)s')
        sh.setLevel(logging.INFO)  # Trying to set custom level for stream handler
        sh.setFormatter(shformat)
        logger.addHandler(sh)

        # fh = ConcurrentRotatingFileHandler(logfile, maxBytes=maxKB*1024, backupCount=5)
        # fhformat = logging.Formatter(
        #     '%(asctime)-15s | %(name)s | %(filename)s | %(funcName)s | %(lineno)d |  %(levelname)s | %(message)s')
        # fh.setLevel(logging.DEBUG)  # Trying to set custom level for file handler
        # fh.setFormatter(fhformat)
        # logger.addHandler(fh)

        # logger.info("set log file {} to {}".format(name + '.log', path))

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # For unknown exceptions
    sys.excepthook = handle_exception

    return logger


# logger = setupLogger(name='logger', level=logging.DEBUG)