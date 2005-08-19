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

    def __init__(self,start_value, end_value):
        QwtScaleDraw.__init__(self)
        self.start_value = start_value
        self.end_value = end_value
        self.delta = self.end_value - self.start_value
    # __init__()

    def label(self,v):
        if v - self.start_value > self.delta:
          v = v - self.delta
        return QwtScaleDraw.label(self,v)

