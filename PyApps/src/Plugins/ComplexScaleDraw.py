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

    def draw(self, painter):
        # 1. paint real value ticks as done in C++ code
        # 2. paint imag value ticks with the shift depending on
        #    the dimension and tick spacing
        # 3. draw backbone, if needed
        # need to understand QwtScaleDiv

        d_scldiv = QwtScaleDraw.scaleDiv(self)
        d_majLen = QwtScaleDraw.majTickLength(self)
        d_minLen = 4         # not directly accessible by a function call
                             # use default as given in c++ equivalent
        d_medLen = 6         # not directly accessible by a function call
                             # use default as given in c++ equivalent
        step_eps = 1.0e-6    # constant value in the c++ equivalent
        Backbone = True      # try out False and see what happens
        self.offset = 0
# plot major ticks
        for i in range(d_scldiv.majCnt()):
            val = d_scldiv.majMark(i)
            v = val % self.divisor
            if self.offset == 0 and v != val:
              self.offset = d_scldiv.majStep() - v % d_scldiv.majStep()
            val = val + self.offset
            QwtScaleDraw.drawTick(self,painter, val, d_majLen)
            QwtScaleDraw.drawLabel(self,painter, val)
# finally, in this case plot a major tick at the dividing point
        QwtScaleDraw.drawTick(self,painter, self.divisor, d_majLen)
        QwtScaleDraw.drawLabel(self,painter,self.divisor)

# can't handle logs properly, but so what?
        if d_scldiv.logScale():
            for i in range(d_scldiv.minCnt()):
                QwtScaleDraw.drawTick(self,painter, d_scldiv.minMark(i), d_minLen)
        else:
            kmax = d_scldiv.majCnt() - 1
            if kmax > 0:
                majTick = d_scldiv.majMark(0)
                hval = majTick - 0.5 * d_scldiv.majStep()
                k = 0
                for i in range(d_scldiv.minCnt()):
                    val = d_scldiv.minMark(i)
                    if  val > majTick:
                        if k < kmax:
                            k = k + 1
                            majTick = d_scldiv.majMark(k)
                        else:
                            majTick += d_scldiv.majMark(kmax) + d_scldiv.majStep()
                        hval = majTick - 0.5 * d_scldiv.majStep()
                    if val >= self.divisor:
                      val = val + self.offset
                    if val > 2 * self.divisor:
                      val = val - self.divisor
                    if abs(val-hval) < step_eps * d_scldiv.majStep():
                        QwtScaleDraw.drawTick(self,painter, val, d_medLen)
                    else:
                        QwtScaleDraw.drawTick(self,painter, val, d_minLen)

        if QwtScaleDraw.options(self) and Backbone:
            QwtScaleDraw.drawBackbone(self,painter)


class ComplexScaleSeparate (QwtScaleDraw):

    def __init__(self,start_value, end_value):
        QwtScaleDraw.__init__(self)
        self.start_value = start_value
        self.end_value = end_value
        self.delta = self.end_value - self.start_value
    # __init__()

    def label(self,v):
        if v >= self.end_value:
          v = v - self.delta
        return QwtScaleDraw.label(self,v)

    def draw(self, painter):
        # 1. paint real value ticks as done in C++ code
        # 2. paint imag value ticks with the shift depending on
        #    the dimension and tick spacing
        # 3. draw backbone, if needed
        # need to understand QwtScaleDiv

        d_scldiv = QwtScaleDraw.scaleDiv(self)
        d_majLen = QwtScaleDraw.majTickLength(self)
        d_minLen = 4         # not directly accessible by a function call
                             # use default as given in c++ equivalent
        d_medLen = 6         # not directly accessible by a function call
                             # use default as given in c++ equivalent
        step_eps = 1.0e-6    # constant value in the c++ equivalent
        Backbone = True      # try out False and see what happens
        self.offset = 0
        self.divisor = self.end_value
# plot major ticks
        for i in range(d_scldiv.majCnt()):
            val = d_scldiv.majMark(i)
            v = val 
            if val >= self.end_value:
              v = val - self.delta
            if self.offset == 0 and v != val:
              self.offset = d_scldiv.majStep() - v % d_scldiv.majStep()
            val = val + self.offset
            QwtScaleDraw.drawTick(self,painter, val, d_majLen)
            QwtScaleDraw.drawLabel(self,painter, val)

# can't handle logs properly, but so what?
        if d_scldiv.logScale():
            for i in range(d_scldiv.minCnt()):
                QwtScaleDraw.drawTick(self,painter, d_scldiv.minMark(i), d_minLen)
        else:
            kmax = d_scldiv.majCnt() - 1
            if kmax > 0:
                majTick = d_scldiv.majMark(0)
                hval = majTick - 0.5 * d_scldiv.majStep()
                k = 0
                for i in range(d_scldiv.minCnt()):
                    val = d_scldiv.minMark(i)
                    if  val > majTick:
                        if k < kmax:
                            k = k + 1
                            majTick = d_scldiv.majMark(k)
                        else:
                            majTick += d_scldiv.majMark(kmax) + d_scldiv.majStep()
                        hval = majTick - 0.5 * d_scldiv.majStep()
                    if val >= self.end_value:
                      val = val + self.offset
                    if val > 2 * self.divisor:
                      val = val - self.divisor
                    if abs(val-hval) < step_eps * d_scldiv.majStep():
                        QwtScaleDraw.drawTick(self,painter, val, d_medLen)
                    else:
                        QwtScaleDraw.drawTick(self,painter, val, d_minLen)

        if QwtScaleDraw.options(self) and Backbone:
            QwtScaleDraw.drawBackbone(self,painter)

