#!/usr/bin/env python

import time
import atexit
import math

class Timing(object):

    cum = {}

    def __init__(self, **kw):
        self.kw = kw

    def __enter__(self):
        self.name = self.kw.get('name', '!')
        self.name = False if self.name.startswith('!') else self.name
        if self.name:
            self.t0 = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.name:
            Timing.cum[self.name] = (
                    Timing.cum.get(self.name, 0.0) +
                    time.time() - self.t0)

@atexit.register
def timed():
    for k,v in Timing.cum.iteritems():
        print '%20s: %1.3e' % (k, 9+math.log(v))
