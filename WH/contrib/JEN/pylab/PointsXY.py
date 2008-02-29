#!/usr/bin/env python

# file: ../contrib/JEN/pylab/PointsXY.py

# Author: J.E.Noordam
# 
# Short description:
#   Class that holds a set of 2D points, for (pylab) plotting 
#
# History:
#    - 27 jan 2008: creation
#
# Remarks:
#
# Description:
#

#-------------------------------------------------------------------------------

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import pylab
import copy
import random

import PlotStyle



#======================================================================================

class PointsXY (object):
    """Encapsulation of a set of 2D points, for (pylab) plotting
    """

    def __init__(self, yy=None, annot=None, name=None, 
                 xx=None, dyy=None, dxx=None,
                 **kwargs):


        # Deal with the specified name (label):
        self._name = name
        if not isinstance(self._name,str): self._name = '<name>'

        # The PlotStyle specifications are via the kwargs
        self._PlotStyle = PlotStyle.PlotStyle(**kwargs)

        # Extract the relevant keyword arguments from kwargs:
        kw = dict()
        if isinstance(kwargs, dict):
            keys = ['plot_type','plot_mode','plot_naked',
                    'plot_ellipse_stddev','plot_circle_mean',
                    'quiver_scale',
                    'auto_legend','plot_standalone']
            for key in keys:
                if kwargs.has_key(key):
                    kw[key] = kwargs[key]
        kw.setdefault('plot_mode', 'pylab')
        kw.setdefault('plot_type', 'plot')
        kw.setdefault('plot_naked', False)
        kw.setdefault('auto_legend', False)           # <--- !!
        kw.setdefault('plot_grid', True)
        kw.setdefault('plot_standalone', False)
        kw.setdefault('plot_ellipse_stddev', False)
        kw.setdefault('plot_circle_mean', False)
        kw.setdefault('quiver_scale', None)
        self._kw = kw

        # Deal with the specified coordinates:
        self._is_complex = 0
        self._yy = []
        self._xx = []
        self._yarr = None
        self._xarr = None
        self._dyy = []
        self._dxx = []
        self._annot = []
        self._input = dict(annot=annot, dx=dxx, dy=dyy)                      # used in .append()
        self.append(y=yy, annot=annot, x=xx, dx=dxx, dy=dyy, trace=False)     # if any specified 

        # Finished:
        return None

    #---------------------------------------------------------------

    def kwupdate (self, **kwargs):
        """Update self._kw (see .__init__())."""
        if isinstance(kwargs,dict):
            # print 'kwupdate(): ',self.oneliner()
            for key in kwargs.keys():
                if self._kw.has_key(key):
                    was = self._kw[key]
                    self._kw[key] = kwargs[key]
                    # print '** kwupdate():',key,':',was,'->',self._kw[key]
                else:
                    s = '** kwarg key not recognised: '+str(key)
                    raise ValueError,s
        return True


    #---------------------------------------------------------------

    def append (self, y, annot=None, x=None, dy=None, dx=None, trace=False):
        """Add a point (x,y) to the internal group"""

        if trace:
            print '\n** .append():'
            print 'y =',y
            print 'x =',x
            print 'annot =',annot

        if y==None:
            return True

        if isinstance(y, type(pylab.array([]))):
            y = y.tolist()
        if isinstance(x, type(pylab.array([]))):
            x = x.tolist()
        if isinstance(dx, type(pylab.array([]))):
            dx = dx.tolist()
        if isinstance(dy, type(pylab.array([]))):
            dy = dy.tolist()

        if isinstance(y, (list,tuple)):
            # Recursive: append a list of points.
            # First make sure that all inputs are lists:
            if isinstance(y,tuple): y = list(y)
            if isinstance(x,tuple): x = list(x)
            if isinstance(dx,tuple): dx = list(dx)
            if isinstance(dy,tuple): dy = list(dy)
            if isinstance(annot,tuple): annot = list(annot)
            nyy = len(self._yy)
            ny = len(y)
            if ny==0:
                raise ValueError,'** [y] has zero length'
            if not isinstance(x, list):
                x = range(nyy,nyy+ny+1)
            if not isinstance(dx, list):
                if dx==None: dx = 0.0
                dx = ny*[dx]
            if not isinstance(dy, list):
                if dy==None: dy = 0.0
                dy = ny*[dy]
            if not isinstance(annot, list):
                if ny==1: annot = [annot]
                if ny>1: annot = ny*[None]

            # OK: append the points one by one:
            for i,y1 in enumerate(y):
                if trace:
                    print '-',i,': (x,y)=',x[i],y[i],annot[i],' (dx,dy)=',dx[i],dy[i]
                self.append (y=y[i], annot=annot[i], 
                             x=x[i], dy=dy[i], dx=dx[i],
                             trace=trace)
            return True

        #----------------------------------------------------------
        # Append a single point:
        #----------------------------------------------------------

        self._yarr = None
        self._xarr = None

        is_complex = False
        xauto = False
        if isinstance(y, complex):
            if self._kw['plot_type']=='polar':
                self._yy.append(pylab.abs(y))                # amplitude
                self._xx.append(pylab.angle(y))              # phase (rad)
                n = len(self._yy)-1
                print '--',n,':',y,'-> (x,y)',self._xx[n],self._yy[n]
            else:
                self._yy.append(y.imag)
                self._xx.append(y.real)
                is_complex = True
        elif isinstance(y, (float,int)):
            self._yy.append(float(y))
            if isinstance(x, (float,int)):
                self._xx.append(float(x))
            else:                                     
                xauto = True                                 # automatic x
                if False and self._kw['plot_type'] in ['plot','semilogy']:
                    self._xx.append(float(len(self._yy)-1))  # start at 0 (better)
                else:
                    self._xx.append(float(len(self._yy)))    # start at 1 (safer)
        else:
            s = '** .append(): type(y) not recognized: '+str(type(y))
            raise ValueError,s

        # Count the number of complex points:
        if is_complex:
            self._is_complex += 1

        # Then the error-bars:
        if isinstance(dy, complex):
            self._dyy.append(dy.imag)
            self._dxx.append(dy.real)

        else:
            dyin = self._input['dy']                   # see .__init__()
            if isinstance(dy, (float,int)):
                self._dyy.append(float(dy))
            elif isinstance(dyin, (float,int)):
                self._dyy.append(float(dyin))
            else:
                self._dyy.append(0.0)

            dxin = self._input['dx']                   # see .__init__()
            if xauto:                                  # automatic x (0,1,2,...)
                self._dxx.append(0.0)                  # no x-error-bar
            elif isinstance(dx, (float,int)):
                self._dxx.append(float(dx))
            elif is_complex:
                dylast = self._dyy[len(self._dyy)-1]
                self._dxx.append(dylast)
            elif isinstance(dxin, (float,int)):
                self._dxx.append(float(dxin))
            else:
                self._dxx.append(0.0)


        # Point annotations: 
        if annot==None:
            annin = self._input['annot']               # see .__init__()
            if annin==None or annin==False:
                self._annot.append(None)
            elif isinstance(annin, bool):
                self._annot.append(len(self._yy)-1)
            else:
                self._annot.append(str(annin))
        else:
            self._annot.append(str(annot))

        if trace:
            print '** PointsXY.append(',x,y,dx,dy,annot,')'
        return True



    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <PointsXY> '+self.name()+':'
        ss += ' n='+str(self.len())
        if self._is_complex:
            ss += ' (complex'
            if not (self._is_complex==self.len()):
                ss += ':'+str(self._is_complex)+'!'
            ss += ')'
        ss += ' '+self._PlotStyle.summary()
        ss += '  yrange='+format_float(self.yrange())
        ss += '  xrange='+format_float(self.xrange())
        ss += '  plot_type='+str(self._kw['plot_type'])
        return ss

    def display(self, txt=None):
        """Display the contents of this obkect"""
        print '\n** '+str(txt)+':'
        print '** ',self.oneliner()
        print ' * yy:    ',self.sumarr(self._yy)
        print ' * xx:    ',self.sumarr(self._xx)
        print ' * yarr:  ',self.sumarr(self.yy())
        print ' * xarr:  ',self.sumarr(self.xx())
        print ' * dyy:   ',self.sumarr(self._dyy)
        print ' * dxx:   ',self.sumarr(self._dxx)
        print ' * annot: ',self.sumarr(self._annot)
        print ' * ',self._PlotStyle.oneliner()
        print '**\n'
        return True

    def sumarr(self, arr):
        """Helper function to format the summary of the given array"""
        s = str(len(arr))+'/'+str(self.len())
        s += ' '+str(type(arr))
        if len(arr)>0:
            s += ' elem[0] ('+str(type(arr[0]))+'):'
            s += ' = '+str(arr[0])
        return s
    

    #===============================================================
    # Access routines:
    #===============================================================

    def len(self):
        """Return the length (nr of points)"""
        return len(self._yy)

    def name(self):
        """Return the name (label?) of this set of points"""
        return self._name

    #------------------------------------------------

    def yy(self, arr=True):
        """Return the y-coordinate(s) in the specified format."""
        if not arr: return self._yy
        if self._yarr==None:
            self._yarr = pylab.array(self._yy)
        return self._yarr

    def yrange(self, margin=0.0, yrange=None):
        """Return [min,max] of the y-coordinate(s)."""
        return self._range(self.yy(), self._dyy, margin=margin, vrange=yrange)

    def __getitem__(self, index):
        """Return the coordinates [x,y] of the specified (index) point"""
        return [self._xx[index],self._yy[index]]

    def mean(self, mode='y'):
        """Return the mean of the specified coordinates:
        - mode=y: -> mean(yy) (default)
        - mode=x: -> mean(xx)
        - mode=r: -> sqrt(mean(xx)**2+mean(yy)**2)
        - mode=rr: -> mean(r)
        - mode=xy: -> [mean(xx),mean(yy)]"""
        if mode=='y': return pylab.mean(self._yy)
        if mode=='xy': return [pylab.mean(self._xx),pylab.mean(self._yy)]
        if mode=='r': return (pylab.mean(self._xx)**2+pylab.mean(self._yy)**2)**0.5
        if mode=='rr':
            return pylab.mean(((self.xx()**2)+(self.yy()**2))**0.5)
        if mode=='x': return pylab.mean(self._xx)
        return None

    def stddev(self, mode='y'):
        """Return the stddev of the specified coordinates:
        - mode=y: -> stddev(yy) (default)
        - mode=x: -> stddev(xx)
        - mode=xy: -> [stddev(xx),stddev(yy)]"""
        if self.len()==1:
            if mode=='xy': return [0.0,0.0]
            return 0.0
        if mode=='y': return self.yy().stddev()
        if mode=='xy': return [self.xx().stddev(),self.yy().stddev()]
        if mode=='x': return self.xx().stddev()
        return None


    #------------------------------------------------

    def xx(self, arr=True):
        """Return the x-coordinate(s) in the specified format."""
        if not arr: return self._xx
        if self._xarr==None:
            self._xarr = pylab.array(self._xx)
        return self._xarr

    def xrange(self, margin=0.0, xrange=None):
        """Return [min,max] of the x-coordinate(s)."""
        return self._range(self.xx(), self._dxx, margin=margin, vrange=xrange)

    #------------------------------------------------

    def _range(self, vv, dvv=None, margin=0.0, vrange=None):
        """Return [min,max] of the y-coordinate(s).
        Take any margin (error-bar or arrow) into account.
        An extra margin (fraction of the span) may be specified.
        If an existing range [min,max] is specified, take it into account."""
        if vv==None or len(vv)==0:
            return [-0.1,0.1]
        vmin = min(vv)
        vmax = max(vv)
        if isinstance(dvv,list):
            vmin -= abs(min(dvv))
            vmax += abs(max(dvv))
        if margin>0.0:
            dv2 = 0.5*(vmax-vmin)*margin
            if vmax==vmin:
                dv2 = 0.0004
                if not vmax==0.0:
                    dv2 *= vmax
            vmin -= dv2
            vmax += dv2
        if isinstance(vrange,(list,tuple)):
            vmin = min(vrange[0],vmin)
            vmax = max(vrange[1],vmax)
        return [vmin,vmax]


    #===============================================================
    # Modifying operations on the group of points
    #===============================================================

    def shift(self, dy=0.0, dx=0.0):
        """Shift all points by the specified dy and/or (optional) dx"""
        if isinstance(dy,complex):
            dx = real(dy)
            dy = imag(dy)
        if not dy==0.0:
            self._yarr = self.yy() + dy
            self._yy = self._yarr.tolist()
        if not dx==0.0:
            self._xarr = self.xx() + dx
        return [dx,dy]

    #------------------------------------------------

    def rotate(self, angle=0.0, xy0=[0.0,0.0]):
        """Rotate all points by the specified angle (rad),
        around the specified centre xy0=[x0,y0].
        If xy0 is complex, the real and imag parts are used."""
        if not angle==0.0:
            # Make xy0 the origin:
            [x0,y0] = xy2pair(xy0)
            xx = self.xx() - x0
            yy = self.yy() - y0
            # Rotate around the origin:
            sina = pylab.sin(angle)
            cosa = pylab.cos(angle)
            self._xarr = xx*cosa - yy*sina
            self._yarr = xx*sina + yy*cosa
            # Return to the original origin:
            self._xarr += x0
            self._yarr += y0
            # Update the list values also:
            self._xx = self._xarr.tolist()
            self._yy = self._yarr.tolist()
        return True

    #------------------------------------------------

    def magnify(self, factor=1.0, xy0=[0.0,0.0]):
        """Magnify all points by the specified factor,
        w.r.t. the specified centre xy0=[x0,y0].
        If xy0 is complex, the real and imag parts are used."""
        if not factor==1.0:
            [x0,y0] = xy2pair(xy0)
            self._xarr = x0 + (self.xx() - x0)*factor
            self._yarr = y0 + (self.yy() - y0)*factor
            # Update the list values also:
            self._xx = self._xarr.tolist()
            self._yy = self._yarr.tolist()
        return True


    #===============================================================
    #===============================================================
    # Plotting:
    #===============================================================
    #===============================================================

    def plot(self, margin=0.2, dispose='show'):
        """Plot the group of points, using pylab"""

        # Make the label (pleg) to be used for the pylab automatic legend:
        legend_label = '_nolegend_'
        # NB: label=='_nolegend_' causes problems with Qt read SVG....!
        legend_label = None
        pleg = self._kw['auto_legend']
        if pleg:
            if isinstance(pleg,str):
                legend_label = pleg
            elif isinstance(pleg,bool):
                legend_label = self.name()
            else:
                legend_label = str(pleg)

        # Plot the actual points (xx,yy):
        self.plot_points (xx=self.xx(), yy=self.yy(),
                          label=legend_label)

        
        # Annotations and errorbars (if specified):
        self.annotate()
        self.plot_error_bars()                   
                
        # Some optional extras:
        if self._kw['plot_circle_mean']:
            self.plot_circle_mean()
        if self._kw['plot_ellipse_stddev']:
            self.plot_ellipse_stddev()
                
        # Make the window, if required, but AFTER the circles:
        if margin>0.0:
            if self._kw['plot_type']=='plot':
                [xmin,xmax] = self.xrange(margin=margin)
                [ymin,ymax] = self.yrange(margin=margin)
                pylab.axis([xmin, xmax, ymin, ymax])       # <----- !!
            elif self._kw['plot_type']=='polar':
                [rmin,rmax] = self.yrange(margin=margin)
                rr = pylab.array([0.25,0.5,0.75,1.0])*rmax
                labels = []
                for r in rr:
                    labels.append(str(int(r*100)/100.0))
                # labels = ['0.25','0.5','0.75','rmax']
                pylab.rgrids(rr, labels, angle=-90.0)
                # pylab.axis([-rmin, rmax, -rmin, rmax])
                # pylab.axis([0.5, 0.5, -rmax*2.0, rmax*2.0])

        # Make the pylab legend, if required:
        if self._kw['plot_standalone']:
            if self._kw['plot_type']=='polar':
                # pylab.thetagrids(True)                 # see also .rgrids()
                pass
            else:
                # NB: pylab.legend() causes problems with Qwt read svg...!
                if self._kw['auto_legend']: pylab.legend()
                if self._kw['plot_grid']: pylab.grid()  
        
        # Finished:
        if dispose=='show':              # standalone only?
            pylab.show()
        return True

    #---------------------------------------------------------------

    def plot_points(self, xx, yy, label=None, **kwargs):
        """Plot the specified points (xx,yy) with the relevant
        pylab plot (plot, loglog, semilogy, semilogx etc).
        """
        ptype = self._kw['plot_type']
        if ptype=='loglog':
            pylab.loglog(xx, yy, label=label,
                         **self._PlotStyle.kwargs(ptype))
        elif ptype=='semilogy':
            pylab.semilogy(xx, yy, label=label,
                           **self._PlotStyle.kwargs(ptype))
        elif ptype=='semilogx':
            pylab.semilogx(xx, yy, label=label,
                           **self._PlotStyle.kwargs(ptype))
        elif ptype=='polar':
            pylab.polar(xx, yy, label=label,
                        **self._PlotStyle.kwargs(ptype))
        elif ptype=='quiver':
            self.plot_quiver(xx, yy, label=label,
                             **self._PlotStyle.kwargs(ptype))
        elif ptype=='scatter':
            pylab.scatter(xx, yy, label=label,
                          **self._PlotStyle.kwargs(ptype))
        elif self._kw['plot_naked']:
            pylab.plot(xx, yy)
        elif not isinstance(label,str):
            # NB: label=='_nolegend_' causes problems with Qt read SVG....
            pylab.plot(xx, yy,
                       **self._PlotStyle.kwargs('plot'))
        else:
            kwargs = self._PlotStyle.kwargs('plot')
            if kwargs['linestyle']=='.':
                kwargs.__delitem__('linestyle')
                for i,y in enumerate(yy):
                    pylab.plot(xx[i], yy[i], **kwargs)
            else:
                pylab.plot(xx, yy, label=label, **kwargs)
        return True

    #---------------------------------------------------------------

    def plot_quiver(self, xx, yy, label='_nolegend_', **kwargs):
        """Plot the specified arrow(s)
        """
        trace = False
        # trace = True
        if trace:
            print pylab.quiver.func_doc
            print '** plot_quiver(): ',self.oneliner()
            # self.display('plot_quiver()')
        n = len(yy)
        X = pylab.array([xx,xx])
        Y = pylab.array([yy,yy])
        U = pylab.array([self._dxx,n*[0.0]])
        V = pylab.array([self._dyy,n*[0.0]])
        # The following has no effect....
        # U = pylab.array([self._dxx,self._dxx])
        # V = pylab.array([self._dyy,self._dyy])
        if self._kw['quiver_scale']==None:
            S = pylab.sqrt((self._dxx[0]**2)+(self._dyy[0]**2))
        elif isinstance(self._kw['quiver_scale'],(float,int)):
            S = self._kw['quiver_scale']
        elif self._kw['quiver_scale']=='disable':
            # When the automatic scaling is disabled (S=0), there is no arrow-head.
            S = 0.0 
        else:
            # With default scaling (S=1), the arrow is too short by sqrt(dx**2+dy**2)
            S = 1.0
        color = self._PlotStyle.color()
        width = 1.0
        if trace:
            print '  - S =',S,color,width
            print '  - X =',X
            print '  - Y =',Y
            print '  - U =',U
            print '  - V =',V
        pylab.quiver(X,Y,U,V,S, color=color, width=width)
        # pylab.quiver(X,Y,U,V, color=color)
        if trace:
            # pylab.plot(xx,yy,marker='o',color=color)
            print '  - xrange =',self.xrange()
            print '  - yrange =',self.yrange()
        return True

    #---------------------------------------------------------------

    def annotate(self, trace=False):
        """Annotate the points"""
        if not isinstance(self._annot,list): return False
        if not len(self._annot)==self.len(): return False
        kwargs = self._PlotStyle.kwargs('text')
        if trace: print '\n** annotate(): kwargs(text) =',kwargs
        for i in range(self.len()):
            if not self._annot[i]==None:              # ignore if None
                x = self._xx[i]
                y = self._yy[i]
                s = '.  '+str(self._annot[i])
                if trace:
                    print '-',i,':',s,'  x,y =',x,y
                pylab.text(x,y, s, **kwargs)
        if trace: print
        return True

    #---------------------------------------------------------------

    def plot_error_bars(self):
        """Plot vertical and/or horizontal errorbars, if specified"""
        if self._kw['plot_type']=='plot':
            color = self._PlotStyle.color()
            for i,y in enumerate(self._yy):
                x = self._xx[i]
                if self._dyy:
                    dy = self._dyy
                    if isinstance(dy,list): dy = dy[i]
                    dy2 = dy/2.0
                    pylab.plot([x,x], [y-dy2,y+dy2],
                               # label='_nolegend_',
                               color=color, linestyle='-')
                if self._dxx:
                    dx = self._dxx
                    if isinstance(dx,list): dx = dx[i]
                    dx2 = dx/2.0
                    pylab.plot([x-dx2,x+dx2], [y,y],
                               # label='_nolegend_',
                               color=color, linestyle='-')
        return True

    #---------------------------------------------------------------

    def plot_circle_mean(self):
        """Plot a circle around the origin, through [xmean,ymean]"""
        if self._kw['plot_type']=='plot':
            color = self._PlotStyle.color()
            if self._is_complex:
                radius = self.mean('rr')
            else:
                radius = self.mean('r')
            self.plot_ellipse(xy0=[0.0,0.0], a=radius,
                              # label='_nolegend_',
                              color=color, linestyle='--')
            [xmean,ymean] = self.mean('xy')
            if False:
                pylab.text(xmean, ymean, '  mean', color=color)
            if False:
                arr = pylab.Arrow(0,0,xmean,ymean, edgecolor='black',
                                  # label='_nolegend_',
                                  facecolor=color, linewidth=1, alpha=0.05)
                pylab.gca().add_patch(arr)
        return True

    #..............................................................

    def plot_ellipse_stddev(self):
        """Plot an ellipse to mark the (x,y) sttdev"""
        if self._kw['plot_type']=='plot':
            color = self._PlotStyle.color()
            [xmean,ymean] = self.mean('xy')
            [xstddev,ystddev] = self.stddev('xy')
            self.plot_ellipse(xy0=[xmean,ymean], a=xstddev, b=ystddev,
                              # label='_nolegend_',
                              color=color, linestyle='--')
            pylab.plot([xmean], [ymean], marker='+',
                       # label='_nolegend_',
                       markeredgecolor=color, markersize=20)
            pylab.plot([xmean], [ymean], marker='o',
                       # label='_nolegend_',
                       markeredgecolor=color, markerfacecolor=color)
        return True

    #..............................................................

    def plot_ellipse(self, xy0=[0.0, 0.0], a=1.0, b=None,
                     label='_nolegend_',
                     color='red', linestyle='--'):
        """Make an ellipse with given centre(x0,y0) and half-axes a and b.
        If b==None (default), make a circle with radius a."""
        [x0,y0] = xy2pair(xy0)
        xx = []
        yy = []
        if b==None: b = a                 # circle 
        na = 30
        angles = 2*pylab.pi*pylab.array(range(na))/float(na-1)
        for angle in angles:
            xx.append(x0+a*pylab.cos(angle))
            yy.append(y0+b*pylab.sin(angle))
        pylab.plot(xx, yy, color=color,
                   # label=label,
                   linestyle=linestyle)
        return True










#========================================================================
# Some helper functions that are also available externally:
#========================================================================


def xy2pair(xy, trace=False):
    """Helper function to make sure that xy is a list [x,y]""" 
    if xy==None:
        return [None,None]
    elif isinstance(xy,(list,tuple)):
        if len(xy)==2: return xy
        if len(xy)==1: return [xy[0],xy[0]]
        if len(xy)>2: return [xy[0],xy[1]]
        if len(xy)==0: return [None,None]
    elif isinstance(xy,(int,float)):
        return [xy,xy]
    elif isinstance(xy,complex):
        return [xy.real,xy.imag]
    # Error?
    return [None,None]

#-----------------------------------------------------------
# Helper function:
#-----------------------------------------------------------

def format_float(v, name=None, n=2):
    """Helper function to format a float for printing"""
    if isinstance(v, list):
        s = '['
        for i,v1 in enumerate(v):
            if i>0: s += ', '
            s += format_float(v1)
        s += ']'
    elif isinstance(v, complex):
        s1 = format_float(v.real)
        s2 = format_float(v.imag)
        s = '('+s1+'+'+s2+'j)'
    else:
        q = 100.0
        v1 = int(v*q)/q
        s = str(v1)
    if isinstance(name,str):
        s = name+'='+s
    # print '** format_float(',v,name,n,') ->',s
    return s



#========================================================================
# Some test objects:
#========================================================================


def test_line (n=6, name='test_line', **kwargs):
    """PointsXY object for a straight line"""
    kwargs.setdefault('color','magenta')
    kwargs.setdefault('style','-')
    yy = 0.3*pylab.array(range(1,n))
    # name += '_'+kwargs['plot_type']
    print '\n** ',name,':',kwargs,'\n'
    pts = PointsXY (yy, xx=yy, name=name, **kwargs)
    print pts.oneliner()
    return pts

def test_parabola (n=6, name='test_parabola', **kwargs):
    """PointsXY object for a parabola"""
    kwargs.setdefault('color','blue')
    kwargs.setdefault('style','-')
    kwargs.setdefault('marker','+')
    kwargs.setdefault('markersize',10)
    yy = pylab.array(range(n))/2.0
    yy = -3+yy+yy*yy
    pts = PointsXY (yy, name=name, **kwargs)
    print pts.oneliner()
    return pts

def test_sine (n=10, name='test_sine', **kwargs):
    """PointsXY object for a sine-wave"""
    kwargs.setdefault('color','red')
    kwargs.setdefault('style','--')
    yy = 0.6*pylab.array(range(n))
    yy = pylab.sin(yy)
    pts = PointsXY (yy, name=name, **kwargs)
    print pts.oneliner()
    return pts

def test_cloud (n=10, mean=1.0, stddev=1.0,
                name='test_cloud', **kwargs):
    """PointsXY object for a cloud of random points"""
    kwargs.setdefault('color','green')
    kwargs.setdefault('style','cross')
    kwargs.setdefault('plot_ellipse_stddev',True)
    kwargs.setdefault('plot_circle_mean',True)
    # kwargs.setdefault('markersize',10)
    yy = range(n)
    xx = range(n)
    for i,v in enumerate(yy):
        yy[i] = random.gauss(mean,stddev)
        xx[i] = random.gauss(mean,stddev)
    pts = PointsXY (yy, name=name, xx=xx, **kwargs)
    print pts.oneliner()
    return pts


#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: PointsXY.py:\n'

    kwargs = dict()
    kwargs = dict(color='magenta', style='o', markersize=5, markeredgecolor='blue')
    # kwargs = dict(color='magenta', style='-', marker='o', markersize=5, markeredgecolor='blue')
    # kwargs['linestyle'] = '-'
    kwargs['quiver_scale'] = None
    kwargs['plot_ellipse_stddev'] = True
    kwargs['plot_circle_mean'] = True
    # kwargs['auto_legend'] = True
    kwargs['plot_standalone'] = True
    # kwargs['plot_naked'] = True

    pts = PointsXY(range(6), name='list', annot=True, dxx=2, dyy=1.0, **kwargs)
    if 0:
        pts = PointsXY(name='list', annot=True, dxx=1.3, dyy=1.0, **kwargs)
        for i in range(6):
            pts.append(i,str(i-10))
    if 0:
        yy = range(1,25)
        xx = range(1,25)
        plot_type = 'loglog'
        plot_type = 'semilogx'
        plot_type = 'semilogy'
        plot_type = 'polar'
        # plot_type = 'plot'
        pts = PointsXY(yy, xx=xx, name=plot_type, plot_type=plot_type, **kwargs)
        
    if 0:
        yy = []
        for i in range(1,5):
            yy.append(complex(0.1*i,0.1*i+0.1))
        pts = PointsXY(yy, name='complex_polar', annot=True,
                       plot_type='polar', **kwargs)
    if 0:
        pts = PointsXY(3, xx=25, dxx=10, dyy=-4, name='arrow',
                       plot_type='quiver', **kwargs)
    if 0:
        pts = PointsXY(range(5), xx=range(1,6),
                       dxx=1.0, dyy=-1.0,
                       # dxx=5*[1.0], dyy=5*[-1.0],
                       name='quiver', plot_type='quiver', **kwargs)
        
    # pts = PointsXY(pylab.array(range(6)), name='numarray', **kwargs)
    # pts = PointsXY(-2, name='scalar', **kwargs)
    # pts = PointsXY(3+5j, name='complex scalar', **kwargs)
    pts = PointsXY([3,-2+1.5j], name='complex list', **kwargs)
    # pts = PointsXY([0,0,0,0], name='zeroes', **kwargs)
    # pts = test_line()
    # pts = test_sine()
    # pts = test_parabola()
    # pts = test_cloud()
    # print pts.oneliner()
    pts.display()

    if 0:
        print '- pts[1] -> ',pts[1]
        print '- pts[2] -> ',pts[2]
        print '- .yy() -> ',pts.yy(),type(pts.yy())
        print '- .yy(arr=False) -> ',pts.yy(arr=False),type(pts.yy(arr=False))
        print '- .yrange(margin=0.1) -> ',pts.yrange(margin=0.1)
        print '- .xrange(margin=0.1, xrange=[-2,3]) -> ',pts.xrange(margin=0.1, xrange=[-2,3])
        print '- .mean() -> ',pts.mean()
        print '- .mean(xy) -> ',pts.mean('xy')
        print '- .mean(x) -> ',pts.mean('x')
        print '- .mean(r) -> ',pts.mean('r')
        print '- .mean(z) -> ',pts.mean('z')
        print '- .stddev() -> ',pts.stddev()
        print '- .stddev(xy) -> ',pts.stddev('xy')
        print '- .stddev(x) -> ',pts.stddev('x')

    if 0:
        print '- .shift(dy=-10, dx=100) -> ',pts.shift(dy=-10, dx=100), '\n   ',pts.oneliner()
        print '- .magnify(factor=2.0) -> ',pts.magnify(factor=2.0), '\n   ',pts.oneliner()
        print '- .rotate(angle=0.2) -> ',pts.rotate(angle=0.2), '\n   ',pts.oneliner()
        print '- .rotate(angle=0.2, xy0=[-10,100]) -> ',pts.rotate(angle=0.2, xy0=[-10,100]), '\n   ',pts.oneliner()

    if 1:
        pts.plot()

    if 0:
        print '- .xy2pair([2,3]) -> ',xy2pair([2,3])
        print '- .xy2pair(complex(4,5)) -> ',xy2pair(complex(4,5))
        print '- .xy2pair(3.4) -> ',xy2pair(3.4)
        print '- .xy2pair(None) -> ',xy2pair(None)
        print '- .xy2pair(range(3)) -> ',xy2pair(range(3))
        print '- .xy2pair([4]) -> ',xy2pair([4])
        print '- .xy2pair([]) -> ',xy2pair([])

    print '\n** End of local test of: PointsXY.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


