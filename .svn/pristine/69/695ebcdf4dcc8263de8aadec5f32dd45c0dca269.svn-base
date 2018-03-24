from contextlib import contextmanager

class KeyLock(object):

    def __init__(self):
        self._lockMap = {}

    @contextmanager
    def lock(self, key):
        try:
            yield
        except:
            raise
