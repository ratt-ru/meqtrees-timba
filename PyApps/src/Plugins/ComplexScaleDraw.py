from qt import *
from qwt import *

class ComplexScaleDraw (QwtScaleDraw):

    def __init__(self,divisor):
        QwtScaleDraw.__init__(self)
        self.divisor = divisor
    # __init__()

    def setDivisor(self,divisor):
        self.divisor = divisor

    def label(self,v):
	v = v % self.divisor
        return QwtScaleDraw.label(self,v)

class ComplexScaleSeparate (QwtScaleDraw):

    def __init__(self,start_freq, end_freq):
        QwtScaleDraw.__init__(self)
        self.start_freq = start_freq
        self.end_freq = end_freq
        self.delta = self.end_freq - self.start_freq
    # __init__()

    def label(self,v):
        if v > self.end_freq:
          v = v - self.delta
        return QwtScaleDraw.label(self,v)

