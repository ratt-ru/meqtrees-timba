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
        if v > self.divisor:
          v = v - self.divisor
        return QwtScaleDraw.label(self,v)

