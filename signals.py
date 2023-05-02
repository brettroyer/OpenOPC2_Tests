from PySignal import ClassSignalFactory


class PySignals(object):
    """
    Re-Class of https://github.com/dgovil/PySignal project.
    Note:  Please use v1.1.4 which is not on pip.   Download from github repository and
    install using "python setup.py install"
    """

    # Creates all the signals
    signals = ['progress', 'msg']
    signal = ClassSignalFactory()

    for s in signals:
        signal.register(s)

    def __init__(self, name: str = "Signal"):
        self.name = name

    def __str__(self) -> str:
        return self.name

    @property
    def progress(self) -> signal:
        return self.signal['progress']

    @property
    def msg(self) -> signal:
        return self.signal['msg']


class TestSignal(object):

    signal = PySignals(name="Test_Signals")

    def __init__(self):
        pass

    def run(self):
        self.signal.progress(1)
        self.signal.msg("test message")


def test_msg_cb(msg):
    print(msg)


def test_progress_cb(x):
    print(x)


if __name__ == "__main__":
    t1 = TestSignal()
    t1.signal.progress.connect(test_progress_cb)
    t1.signal.msg.connect(test_msg_cb)
    t1.run()