import os
import uuid
import datetime


class optobjIterator:

    def __init__(self, options):
        # self.options = options
        # self._options = [attr for attr in dir(options) if not callable(getattr(options, attr)) and not attr.startswith("__")]
        # self._values = [getattr(options, attr) for attr in dir(options) if not callable(getattr(options, attr)) and not attr.startswith("__")]
        self._options = [{attr: getattr(options, attr)} for attr in dir(options) if not callable(getattr(options, attr)) and not attr.startswith("__")]
        self._index = 0

    def next(self):
        if self._index < len(self._options):
            result = self._options[self._index]
            self._index += 1
            return result
            # End of Iteration
        raise StopIteration


class optobj(object):

    # OPC Server Options
    opc_test_ok = False
    ip = '192.168.1.100'
    local = False  # TODO:  Replace with new parameter mode using  'gateway' or 'com' for openopc2 library
    mode = 'com'
    svr = 'OPC.DeltaV.1'
    sliceamt = 500
    read_opc = False
    sleepTime = 2

    connected = False  # Set to true if opc (OpenOpc object is created and connected)
    opc = None  # OpenOpc object.
    timeout = 5000  # Opc read timeout
    retry_count = 3   # Number of times OPC read will retry read. Slice amount will reduce by percentage each attempt
    pct_num = 20  # pct_num/100 = %, Number of % slice amount will reduce each attempt.

    # Filter By Options
    filter = "PID"

    # General Options
    coding = 'utf-8'
    # log = None
    selected = None
    debug = False
    progpath = None
    self = None
    date = None
    uuid = None
    readq_timeout = 2  # TODO: is this implemented, on ui or ini?
    style = None
    logging = False  # Enabled True/False

    # Excel Options
    write_to_excel = False
    excel_filename = 'dvutil.xlsx'

    # dB Options
    db = None  # db Object
    dbUse = False  # Disabled overall db functions - enabled/disabled from .ini file
    dbMaster = None  # Master db Object
    dbpath = None  # Path where .db resides for this session
    dbname = None  # Selected .db file name
    dbAdd = False  # Add FHX file to db
    dbUsing = False  # Program is using the db and not a fhx file directly.
    dbWriteSetupdata = False
    dbReadSetupdata = False
    dbReadmodules = False
    dbWritemodules = False
    selected_id = None

    # FHX Options
    filename = ''
    orgfilename = ''
    removeorg = False
    filepath = None
    counter = 0
    version = None
    filedate = None
    modules = None
    converted = False
    lines = 0

    # Setup Data (deprecated)
    classes = None  # Classes with function blocks
    fbdef = None # Function Block Definitions.
    fbtemplates = None  # Function Block Templates
    dynamicrefs = None  # Dynamic References Classes

    # Setup Data
    classes_dict = None  # Classes with function blocks (Dictionary of classes)
    fbdef_dict = None  # Function Block Definitions. (Dictionary of Function Block Definitions.
    fbtemplates_dict = None  # Function Block Templates List
    dynamicrefs_dict = None  # Dynamic References Classes (Dictionary of Dynamic References).

    # Advanced Options
    setupdataran = False
    usedebugfiles = False

    # Text File Options
    opclist = None

    def __init__(self):
        self.progpath = os.getcwd()
        self.date = datetime.datetime.now()

    def __repr__(self):
        members = [attr for attr in dir(optobj) if not callable(getattr(optobj, attr)) and not attr.startswith("__")]
        return str(members)

    def __iter__(self):
        return optobjIterator(self)

    def set_uuid(self):
        self.uuid = str(uuid.uuid1())
        return self.uuid

    def update_ip(self, v):
        self.ip = v

    def update_svr(self, v):
        self.svr = v

    def update_sliceamt(self, v):
        self.sliceamt = v

    def update_read_opc(self, v):
        self.read_opc = v

    def update_local(self, v):
        self.local = v

    def update_debug(self, v):
        self.debug = v

    def update_filename(self, v):
        self.filename = v

    def update_db(self, v):
        self.dbUse = v
        if v:
            self.self.ui.seldb.setEnabled(False)
        else:
            self.self.ui.seldb.setEnabled(True)

    def update_write_to_excel(self, v):
        self.write_to_excel = v

    def update_timeout(self, v):
        self.timeout = v

    def update_retry(self, v):
        self.retry_count = v

    def update_pct(self, v):
        self.pct_num = v

    def update_removeorg(self, v):
        self.removeorg = v


if __name__ == "__main__":
    options = optobj()
    for option in options:
        print (option)