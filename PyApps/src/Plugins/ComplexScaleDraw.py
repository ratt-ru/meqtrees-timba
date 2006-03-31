from qt import *
from qwt import *

class ComplexScaleDraw(QwtScaleDraw):

    def __init__(self,divisor):
        QwtScaleDraw.__init__(self)
        self.divisor = divisor
    # __init__()

    def setDivisor(self,divisor):
        self.divisor = divisor

    def label(self,v):
	v = v % self.divisor
        return QwtScaleDraw.label(self,v)
    # label()

    def draw(self, painter):
        # 1. paint real value ticks as done in C++ code
        # 2. paint imag value ticks with the shift depending on
        #    the dimension and tick spacing
        # 3. draw backbone, if needed

        step_eps = 1.0e-6    # constant value in the c++ equivalent
        scldiv = QwtScaleDraw.scaleDiv(self)
        majLen, medLen, minLen = QwtScaleDraw.tickLength(self)
        self.offset = 0
        # plot major ticks
        for i in range(scldiv.majCnt()):
            val = scldiv.majMark(i)
            v = val % self.divisor
            if self.offset == 0 and v != val:
              self.offset = scldiv.majStep() - v % scldiv.majStep()
            val = val + self.offset
            QwtScaleDraw.drawTick(self, painter, val, majLen)
            QwtScaleDraw.drawLabel(self, painter, val)

        # also, plot a major tick at the dividing point
        QwtScaleDraw.drawTick(self,painter, self.divisor, majLen)
        QwtScaleDraw.drawLabel(self,painter,self.divisor)

        # probably can't handle logs properly??
        if scldiv.logScale():
            for i in range(scldiv.minCnt()):
                QwtScaleDraw.drawTick(
                    self, painter, scldiv.minMark(i), minLen)
        else:
            # do minor ticks
            kmax = scldiv.majCnt() - 1
            if kmax > 0:
                majTick = scldiv.majMark(0)
                hval = majTick - 0.5 * scldiv.majStep()
                k = 0
                for i in range(scldiv.minCnt()):
                    val = scldiv.minMark(i)
                    if  val > majTick:
                        if k < kmax:
                            k = k + 1
                            majTick = scldiv.majMark(k)
                        else:
                            majTick += (scldiv.majMark(kmax)
                                        + scldiv.majStep())
                        hval = majTick - 0.5 * scldiv.majStep()
                    if val >= self.divisor:
                      val = val + self.offset
                    if val > 2 * self.divisor:
                      val = val - self.divisor
                    if abs(val-hval) < step_eps * scldiv.majStep():
                        QwtScaleDraw.drawTick(self,painter, val, medLen)
                    else:
                        QwtScaleDraw.drawTick(self, painter, val, minLen)

        if QwtScaleDraw.options(self) & QwtScaleDraw.Backbone:
            QwtScaleDraw.drawBackbone(self, painter)

    # draw()
# class ComplexScaleDraw()

class ComplexScaleSeparate(QwtScaleDraw):

    def __init__(self, start_value, end_value):
        QwtScaleDraw.__init__(self)
        self.start_value = start_value
        self.end_value = end_value
        self.delta = self.end_value - self.start_value

    # __init__()

    def label(self, v):
        if v >= self.end_value:
            v = v - self.delta
        return QwtScaleDraw.label(self, v)

    # label()

    def draw(self, painter):
        # 1. paint real value ticks as done in C++ code
        # 2. paint imag value ticks with the shift depending on
        #    the dimension and tick spacing
        # 3. draw backbone, if needed

        step_eps = 1.0e-6    # constant value in the c++ equivalent
        scldiv = QwtScaleDraw.scaleDiv(self)
        majLen, medLen, minLen = QwtScaleDraw.tickLength(self)
        self.offset = 0
        self.separator = self.end_value
        # plot major ticks
        for i in range(scldiv.majCnt()):
            val = scldiv.majMark(i)
            v = val
            if val >= self.end_value:
                v = val - self.delta
            if self.offset == 0 and v != val:
                self.offset = scldiv.majStep() - v % scldiv.majStep()
            val = val + self.offset
            QwtScaleDraw.drawTick(self, painter, val, majLen)
            QwtScaleDraw.drawLabel(self, painter, val)

        # also, plot a major tick at the dividing point
        QwtScaleDraw.drawTick(self,painter, self.separator, majLen)
        QwtScaleDraw.drawLabel(self,painter,self.separator)

        # probably can't handle logs properly??
        if scldiv.logScale():
            for i in range(scldiv.minCnt()):
                QwtScaleDraw.drawTick(
                    self, painter, scldiv.minMark(i), minLen)
        else:
            # do minor ticks
            kmax = scldiv.majCnt() - 1
            if kmax > 0:
                majTick = scldiv.majMark(0)
                hval = majTick - 0.5 * scldiv.majStep()
                k = 0
                for i in range(scldiv.minCnt()):
                    val = scldiv.minMark(i)
                    if  val > majTick:
                        if k < kmax:
                            k = k + 1
                            majTick = scldiv.majMark(k)
                        else:
                            majTick += (scldiv.majMark(kmax)
                                        + scldiv.majStep())
                        hval = majTick - 0.5 * scldiv.majStep()
                    if val >= self.end_value:
                        val = val + self.offset
                    if val > 2 * self.separator:
                        val = val - self.separator
                    if abs(val-hval) < step_eps * scldiv.majStep():
                        QwtScaleDraw.drawTick(self,painter, val, medLen)
                    else:
                        QwtScaleDraw.drawTick(self, painter, val, minLen)

        if QwtScaleDraw.options(self) & QwtScaleDraw.Backbone:
            QwtScaleDraw.drawBackbone(self, painter)

    # draw()
# class ComplexScaleSeparate()

