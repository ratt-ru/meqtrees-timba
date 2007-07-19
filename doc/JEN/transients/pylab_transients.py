#!/usr/bin/env python

# file: ../doc/JEN/transients/pylab_transient.py


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
# from pylab import *


#-------------------------------------------------------------------------------

def sine_mosaic(**ctrl):
    funcname = on_entry(ctrl, 'sine_mosaic')
    sine_plot(subplot=321)
    sine_plot(subplot=322)
    sine_plot(subplot=323)
    sine_plot(subplot=324)
    sine_plot(subplot=325)
    return on_exit(ctrl, mosaic=True)

#-------------------------------------------------------------------------------

def sine_plot(**ctrl):
    """Illustrate the feasability of sine-interpolation"""
    funcname = on_entry(ctrl, 'sine_plot',
                        xlabel='v-coordinate',
                        ylabel='source contribution (corrugation)',
                        title='sampling visibility corrugations')
    a1 = 1.0
    a2 = 0.5
    P1 = 1.0
    P2 = 4.0
    phoff = 0.2
    xx = pylab.arange(-2, 10, 0.1)
    plot_line(ctrl, xx, a1*pylab.sin(phoff+xx/P1), color='red', labelpos='start',
              label='short period: source far from field centre, or long baseline')
    plot_line(ctrl, xx, a2*pylab.sin(phoff+xx/P2), color='blue', labelpos='start',
              label='long period: source close to field centre, or short baseline')
    kk = pylab.arange(35, 80, 8)
    plot_marker(ctrl, xx[kk], a1*pylab.sin(phoff+xx[kk]/P1), style='o', color='red',
                label=[None,'t-dt','t','t+dt'])
    plot_marker(ctrl, xx[kk], a2*pylab.sin(phoff+xx[kk]/P2), style='o', color='blue',
                label=[None,'t-dt','t','t+dt'], labelpos='top left')
    auxinfo(ctrl, 'first', 1)
    auxinfo(ctrl, 'second', 2)

    if False:
        subsin(**ctrl)

    return on_exit(ctrl)



def subsin(**ctrl):
    """Test function"""
    funcname = on_entry(ctrl, 'subsin',
                        xlabel='x',
                        ylabel='y',
                        title='test')
    a1 = 4.0
    P1 = 1.5
    xx = pylab.arange(-2, 10, 0.1)
    plot_line(ctrl, xx, a1*pylab.sin(xx/P1), color='green', labelpos='start',
              label='subsin')
    auxinfo(ctrl, 'subsin', 1.89)
    return on_exit(ctrl)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def errfac (R_deg=1.0, dt=1.0, b=2000, wvl=2.0, sinDEC=1.0, trace=False):
    """Helper function to calculate the subtraction error factor"""
    epsilon = 2*pylab.pi*(b/wvl)*(dt/(240.0*57.0))*sinDEC*(R_deg/57.0)
    return 1-pylab.cos(epsilon)

#-------------------------------------------------------------------------------



def err_vs_RR_dt_mosaic(b=1000, wvl=2, Rmax=10, dt=[1,2,5,10], fsinc=True, **ctrl):
    funcname = on_entry(ctrl, 'err_vs_RR_dt_mosaic')
    err_vs_RR_dt(subplot=221, b=b, wvl=2, Rmax=5, dt=dt, fsinc=fsinc, title='LOFAR core')
    err_vs_RR_dt(subplot=223, b=b, wvl=2, Rmax=5, dt=dt, fsinc=fsinc, title='LOFAR core', zoom=True)
    err_vs_RR_dt(subplot=222, b=b, wvl=0.21, Rmax=0.5, dt=dt, fsinc=fsinc, title='WSRT')
    err_vs_RR_dt(subplot=224, b=b, wvl=0.21, Rmax=0.5, dt=dt, fsinc=fsinc, title='WSRT', zoom=True)
    return on_exit(ctrl, mosaic=True)
    

#-------------------------------------------------------------------------------

def err_vs_RR_dt(b=500, wvl=2, Rmax=5, dt=[1,2,5,10], fsinc=True, zoom=False, **ctrl):
    """Plot the subtraction error factor vs source position,
    as a function of subtraction interval dt"""
    funcname = on_entry(ctrl, 'err_vs_RR_dt',
                        xlabel='distance (deg!) from field centre',
                        ylabel='residual fraction:  1-cos(e)',
                        title='source subtraction error (worst case)')
    # auxinfo(ctrl, 'case', case)
    auxinfo(ctrl, 'average baseline', b, unit='m')
    auxinfo(ctrl, 'lambda', wvl, unit='m')
    auxinfo(ctrl, 'dt', dt, unit='s')
    RR = pylab.arange(0.01,Rmax*3,float(Rmax)/20)
    n = len(RR)-1
    if fsinc:
        # Optonal, apply the freq-averaging sinc:
        RRsinc = pylab.pi*RR/(2*Rmax)
        sinc = pylab.sin(RRsinc)/RRsinc
        plot_line(ctrl, RR, sinc, color='magenta', style='dashed', width=2,
                  labelpos='start', label='freq-averaging sinc')
        fbw = 57*(float(wvl)/float(b))/Rmax
        auxinfo(ctrl, 'required fractional bw', fbw)
    emax = 0.01
    for dt1 in dt:
        ee = errfac (R_deg=RR, dt=dt1, b=b, wvl=wvl, sinDEC=1.0) 
        plot_line(ctrl, RR, ee, color='red', style='dashed',
                  labelpos='end', label='dt = '+str(dt1)+' s')
        if fsinc:
            plot_line(ctrl, RR, ee*sinc, color='green',
                      labelpos='end', label='dt = '+str(dt1)+' s')
    plot_line(ctrl, [0.0,max(RR)], [emax,emax], color='blue',
              labelpos='start', label='one percent error')
    if zoom:
        ctrl['window'] = dict(ymin=-emax, ymax=emax*3)
    return on_exit(ctrl)





#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

def uv_corrug(lm=[1.25,2], color='yellow', domain=True, **ctrl):
    """Plot the sinusoidal corrugation of a source of given position"""
    funcname = on_entry(ctrl, 'uv_corrug')
    rr = dict()
    umax = 200
    vmax = umax
    if domain:
        uv_track(umin=umax/2, sinDEC=0.5, frab=0.1, dt=1.0, show=False)
        uv_domain(umin=umax/2, sinDEC=0.5, frab=0.1, HA=1.0, dt=1.0, show=False)
    kk = range(-20,20)
    slope = -float(lm[0])/float(lm[1])         # -l/m
    for k in kk:
        u1 = -umax
        u2 = umax
        v1 = u1*slope + k*2*pylab.pi
        v2 = u2*slope + k*2*pylab.pi
        pylab.plot([u1,u2], [v1,v2], color=color)
    pylab.plot([0.0,0.0], [-vmax,vmax], color='blue')
    pylab.plot([-umax,umax], [0.0,0.0], color='blue')
    pylab.axis([-umax, umax, -vmax, vmax])
    pylab.xlabel('u-coordinate (wavelengths)')
    pylab.ylabel('v-coordinate (wavelengths)')
    pylab.title('uv-plane corrugation')
    auxinfo(xmin=-umax, ymax=vmax, ymin=-vmax, xmax=umax,
            subplot=ctrl['subplot'],
            ss=['(l,m) = '+str(lm)+' deg'])
    return on_exit(ctrl)


#--------------------------------------------------------------------------

def uv_domain(umin=100, sinDEC=0.5, frab=0.1, HA=1.0, dt=1.0, color='blue', **ctrl):
    """Draw a request domain with the required characteristics"""
    funcname = on_entry(ctrl, 'uv_domain')
    vmin = umin*sinDEC
    frab_factor = 1.0 + frab
    draw_ellipse(0,0, a=[umin,umin*frab_factor],
                 b=[vmin,vmin*frab_factor],
                 pmin=HA, pmax=HA+dt/(240*57),
                 color=color)
    return on_exit(ctrl)

#--------------------------------------------------------------------------

def uv_track(umin=100, sinDEC=0.5, frab=0.1, **ctrl):
    """Draw a uv-track with the required characteristics"""
    funcname = on_entry(ctrl, 'uv_track')
    vmin = umin*sinDEC
    frab_factor = 1.0 + frab
    draw_ellipse(0,0, a=[umin,umin*frab_factor],
                 b=[vmin,vmin*frab_factor])
    return on_exit(ctrl)

#-------------------------------------------------------------------------------
# Plotting helper functions
#-------------------------------------------------------------------------------

def on_entry(ctrl=dict(), funcname='<funcname>',
             xlabel='<xlabel>', ylabel='<ylabel>', title=None):
    """Helper function called at the start of plot-routines"""
    ctrl.setdefault('funcname', [])
    ctrl['funcname'].append(funcname)      # NB: append....!
    ctrl.setdefault('trace', True)
    ctrl.setdefault('show', True)
    ctrl.setdefault('subplot', None)       # integer: nrow*100+ncol*10+iplot (all 1-relative)
    ctrl.setdefault('iplot', 1)  
    ctrl.setdefault('irow', 1)  
    ctrl.setdefault('icol', 1) 
    ctrl.setdefault('nrow', 1) 
    ctrl.setdefault('ncol', 1) 
    ctrl.setdefault('figure', None) 
    ctrl.setdefault('save', True)
    ctrl.setdefault('savefile', funcname+'.png')
    ctrl.setdefault('rider', dict())
    ctrl.setdefault('auxinfo', [])
    ctrl.setdefault('legend', [])
    ctrl.setdefault('window', None)        # override window (optional)
    ctrl.setdefault('tmargin', 0.10)
    ctrl.setdefault('bmargin', 0.05)
    ctrl.setdefault('lmargin', 0.05)
    ctrl.setdefault('rmargin', 0.05)
    ctrl.setdefault('xlabel', xlabel)
    ctrl.setdefault('ylabel', ylabel)
    ctrl.setdefault('title', funcname)
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
        k = ctrl['subplot']
        ctrl['nrow'] = k/100
        ctrl['ncol'] = (k-100*ctrl['nrow'])/10
        ctrl['iplot'] = k-100*ctrl['nrow']-10*ctrl['ncol']
        ctrl['irow'] = 1+(ctrl['iplot']-1)/ctrl['ncol'] 
        ctrl['icol'] = ctrl['iplot']-ctrl['ncol']*(ctrl['irow']-1)
        print '** subplot:',k
        for key in ['nrow','ncol','iplot','icol','irow']:
            print '-',key,'=',ctrl[key]
        ctrl['save'] = False
        ctrl['show'] = False
    else:
        if isinstance(title, str): ctrl['title'] = title
    if ctrl['trace']: print '\n** on_entry(',funcname,'):',ctrl
    return funcname

#-------------------------------------------------------------------------------

def ctrl_display(ctrl):
    """Helper function to show the contents of the ctrl record"""
    print '\n** JEN_pylab ctrl record:',funcname
    print '- save='+ctrl['save']+' savefile='+ctrl['savefile']
    print '- show='+ctrl['show']
    s = 'subplot=',ctrl['subplot'],' nrow='+ctrl['nrow'],' ncol='+ctrl['ncol']
    print '- '+s+' iplot='+ctrl['iplot']+' irow='+ctrl['irow']+' icol='+ctrl['icol']
    print '-',s
    print
    return True 

def ctrl_field(ctrl, key):
    if not isinstance(key, (list,tuple)): key = [key]
    return ' '+key+'='+str(ctrl[key])

#-------------------------------------------------------------------------------

def on_exit(ctrl=dict(), mosaic=False):
    """Helper function called at the end of plot-routines"""
    if ctrl['trace']: print '\n** on_exit(moasic=',mosaic,'): ctrl =',ctrl,'\n'
    if mosaic:
        ctrl['show'] = True 
    else:
        # Finish the plot:
        if ctrl['subplot']:
            pylab.subplot(ctrl['subplot'])
            tmax = min(len(ctrl['title']), 80/ctrl['ncol'])
            xmax = min(len(ctrl['xlabel']), 80/ctrl['ncol'])
            ymax = min(len(ctrl['ylabel']), 60/ctrl['nrow'])
            pylab.xlabel(ctrl['xlabel'][:xmax])
            if ctrl['icol']==1: pylab.ylabel(ctrl['ylabel'][:ymax])
            if ctrl['irow']==1: pylab.title(ctrl['title'][:tmax])
        else:
            pylab.xlabel(ctrl['xlabel'])
            pylab.ylabel(ctrl['ylabel'])
            pylab.title(ctrl['title'])
        set_window(ctrl)
        show_auxinfo(ctrl)
        if len(ctrl['legend'])>0:
            pylab.legend(ctrl['legend'])
    if ctrl['save']:
        savefile = ctrl['savefile']
        pylab.savefig(savefile)
        print '\n** saved plot in file:',savefile,'\n'
    if ctrl['show']:
        # NB: .show() freezes things until released, so do this last:
        pylab.show()
    return True

#-------------------------------------------------------------------------------

def set_window(ctrl):
    """Set the plot-window"""
    ctrl.setdefault('xmin',-1.0)
    ctrl.setdefault('xmax',1.0)
    ctrl.setdefault('ymin',-1.0)
    ctrl.setdefault('ymax',1.0)

    if isinstance(ctrl['window'], dict):
        # Override with specified window paramters:
        for key in ['xmin','xmax','ymin','ymax']:
            if ctrl['window'].has_key(key):
                ctrl[key] = ctrl['window'][key]
        # Also inhibit auxinfo and legend, assuming zoom....
        ctrl['auxinfo'] = []
        ctrl['legend'] = []

    if True:
        # Make sure of the correct order
        if ctrl['xmax']<ctrl['xmin']:
            xmin = ctrl['xmax']
            ctrl['xmax'] = ctrl['xmin']
            ctrl['xmin'] = xmin
        if ctrl['ymax']<ctrl['ymin']:
            ymin = ctrl['ymax']
            ctrl['ymax'] = ctrl['ymin']
            ctrl['ymin'] = ymin
    if True:
        # Make a small margin in all directions:
        yspan = ctrl['ymax']-ctrl['ymin']
        xspan = ctrl['xmax']-ctrl['xmin']
        if yspan<=0: yspan = 2.0
        if xspan<=0: xspan = 2.0
        ctrl['xmin'] -= xspan*ctrl['lmargin']
        ctrl['xmax'] += xspan*ctrl['rmargin']
        ctrl['ymin'] -= yspan*ctrl['bmargin']
        ctrl['ymax'] += yspan*ctrl['tmargin']
    ctrl['yspan'] = ctrl['ymax']-ctrl['ymin']
    ctrl['xspan'] = ctrl['xmax']-ctrl['xmin']
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    if True:
        # Plot the x and y axes, if appropriate:
        if ctrl['xmin']*ctrl['xmax']<0:
            pylab.plot([ctrl['xmin'], ctrl['xmax']], [0.0,0.0], color='gray')
        if ctrl['ymin']*ctrl['ymax']<0:
            pylab.plot([0.0,0.0], [ctrl['ymin'], ctrl['ymax']], color='gray')
    # NB: Do this LAST (otherwise it makes its own margin....)
    pylab.axis([ctrl['xmin'], ctrl['xmax'], ctrl['ymin'], ctrl['ymax']])
    return True

#-------------------------------------------------------------------------------

def show_auxinfo(ctrl):
    """Helper function to put some lines (ss) of auxiliary information
    into the top left corner of the current plot"""
    dy = ctrl['yspan']/20
    dx = ctrl['xspan']/10
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])                             # e.g. 211,212,...?
        if ctrl['nrow']==2: dy = ctrl['yspan']/15                  # two rows of subplots
        if ctrl['nrow']==3: dy = ctrl['yspan']/10                  # three rows
    y = ctrl['ymax']-2*dy
    for s in ctrl['auxinfo']:
        y -= dy
        pylab.text(ctrl['xmin']+dx,y, str(s), color='gray')
    return True

#-------------------------------------------------------------------------------

def auxinfo(ctrl=dict(), name=None, value=None, unit=None):
    """Append a line to the ctrl[auxinfo] list, for display"""
    s = name
    if not value==None: s += ' = '+str(value)
    if isinstance(unit, str): s += ' ('+unit+')'
    ctrl['auxinfo'].append(s)
    return True

#-------------------------------------------------------------------------------

def adjust_xyrange(ctrl=dict(), xx=None, yy=None):
    """Adjust xy-range in ctrl-record"""
    if not xx==None:
        ctrl.setdefault('xmin', xx[0])
        ctrl.setdefault('xmax', xx[0])
        xx1 = pylab.array(xx)
        ctrl['xmin'] = min(ctrl['xmin'], min(xx1))
        ctrl['xmax'] = max(ctrl['xmax'], max(xx1))
    if not yy==None:
        ctrl.setdefault('ymin', yy[0])
        ctrl.setdefault('ymax', yy[0])
        yy1 = pylab.array(yy)
        ctrl['ymin'] = min(ctrl['ymin'], min(yy1))
        ctrl['ymax'] = max(ctrl['ymax'], max(yy1))
    return True

#-------------------------------------------------------------------------------

def plot_line (ctrl=dict(), xx=[0,1], yy=[0,1], color='red',
               style='-', width=1, label=None, labelpos=None):
    """Plot the given line, and do some bookkeeping"""
    # if not isinstance(xx, (list,tuple,type(pylab.array(0)))): return False
    # if not isinstance(yy, (list,tuple,type(pylab.array(0)))): return False
    adjust_xyrange(ctrl, xx=xx, yy=yy)
    if style=='dashed': style='--'   
    if style=='solid': style='-'
    if style=='dotted': style=':'
    if style=='dashdot': style='-.'
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    pylab.plot(xx, yy, linestyle=style, linewidth=width, color=color)
    if isinstance(label, str):
        n = len(xx)-1
        if isinstance(labelpos, bool):
            labelpos = 'start'
        if not isinstance(labelpos, str):
            ctrl['legend'].append(label)
        elif labelpos=='start':
            pylab.text(xx[0], yy[0], '  '+label, color=color)
        elif labelpos=='end':
            ctrl['rmargin'] = 0.1*(1+ctrl['ncol'])
            pylab.text(xx[n], yy[n], '  '+label, color=color)
    return True


#-------------------------------------------------------------------------------

def plot_marker (ctrl=dict(), xx=0.5, yy=0.5, color='blue',
                 style='o', size=6, label=None, labelpos=None):
    """Plot the given marker(s), and do some bookkeeping"""
    if not isinstance(xx, (list,tuple,type(pylab.array(0)))): xx = [xx]
    if not isinstance(yy, (list,tuple,type(pylab.array(0)))): yy = [yy]
    if not label==None:
        if not isinstance(label, (list,tuple)): label=[label]
    # if not len(xx)==len(yy): return False
    adjust_xyrange(ctrl, xx=xx, yy=yy)
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    # NB: The default is 'bottom' and 'left', which actually places the label
    # at the top-right position of the marker...!
    halign = 'left'                                      # left, right, center 
    valign = 'bottom'                                    # bottom, top, center
    if isinstance(labelpos, str):                        # e.g. ['top right']
        ss = labelpos.split(' ')
        valign = ss[0] 
        halign = ss[1] 
    for i in range(len(xx)):
        pylab.plot([xx[i]], [yy[i]], marker=style,
                   markerfacecolor=color, markersize=size,
                   markeredgecolor=color, markeredgewidth=1)
        if (not label==None) and i<len(label) and (not label[i]==None):
            lstr = '. '+str(label[i])
            if halign=='right': lstr = str(label[i])+' .'
            pylab.text(xx[i], yy[i], lstr, color=color,
                       fontsize=12,
                       horizontalalignment=halign,    
                       verticalalignment=valign)      
    return True

#-------------------------------------------------------------------------------

def show_colors():
    """Helper function to show the available plot colors"""
    print '\n** Available plot-colors:'
    print ' Style 1:'
    print '  b: blue'
    print '  g: green'
    print '  r: red'
    print '  c: cyan'
    print '  m: magenta'
    print '  y: yellow'
    print '  k: black'
    print '  w: white'
    print '  k: black'
    print '  k: black'
    print ' Style 2: standard color string, e.g. yellow, wheat, etc'
    print ' Style 3: grayscale intensity (between 0. and 1., inclusive)'
    print ' Style 4: RGB hex color triple, e.g. #2F4F4F'
    print ' Style 5: RGB tuple, e.g. (0.18, 0.31, 0.31)'
    print
    return True

def show_styles():
    """Helper function to show the available plot styles"""
    print '\n** Available plot-styles:'
    print '  -: solid line'
    print '  --: dashed line'
    print '  :: dotted line'
    print '  -.: dashed-dot line'
    print '--------------------------'
    print '  o: circle'
    print '  s: square'
    print '  +: plus'
    print '  x: cross'
    print '  D: diamond'
    print '  d: thin diamond'
    print '  h: hexagon'
    print '  p: pentagon'
    print '  |: vertical line'
    print '  _: horizontal line'
    print '  ^: up triangle'
    print '  v: down triangle'
    print '  >: right triangle'
    print '  <: left triangle'
    print '  1: up tripod'
    print '  2: down tripod'
    print '  3: right tripod'
    print '  4: left tripod'
    print
    return True

#-------------------------------------------------------------------------------

def rider(ctrl=dict(), item=None, append=None, trace=True):
    """Interaction with rider (arbitrary information) record in ctrl"""
    ctrl.setdefault('rider', dict())
    if not isinstance(ctrl['rider'], dict): ctrl['rider'] = dict()
    if not isinstance(item, str):
        return ctrl['rider']
    ctrl['rider'].setdefault(item, [])
    if not append==None:
        ctrl['rider'][item].append(append)
    return ctrl['rider'][item]
        

#-----------------------------------------------------------------------------

def draw_ellipse(x=0, y=0, a=1, b=None, pmin=0, pmax=None, dp=None, color='red'):
    """Draw an ellipse"""
    x = float(x)
    y = float(y)

    # Determine the number of radial spokes:
    closed = False
    if pmax==None:
        pmax = 2*pylab.pi
        closed = True
    pmax = float(pmax)
    pmin = float(pmin)
    if dp==None:
        dp = (pmax-pmin)/16
        if dp>0.1: dp = 0.1
    if closed:
        pp = pylab.arange(pmin,pmax+dp,dp)
    else:
        pp = pylab.arange(pmin,pmax,dp)

    # Draw two or more concentric ellipses:
    if not isinstance(a, (list,tuple)): a = [0.0,a]
    if b==None: b = a
    if not isinstance(b, (list,tuple)): b = [0.0,b]
    for i in range(len(a)):
        xx = []
        yy = []
        for p in pp:
            xx.append(x+a[i]*pylab.cos(p))
            yy.append(y+b[i]*pylab.sin(p))
            pylab.plot(xx, yy, color=color)
        xx2 = xx
        yy2 = yy
        if i==0:
            xx1 = xx
            yy1 = yy
    if not closed:
        n = len(xx)-1
        pylab.plot([xx1[0],xx2[0]], [yy1[0],yy2[0]], color=color, linestyle='-')
        pylab.plot([xx1[n],xx2[n]], [yy1[n],yy2[n]], color=color, linestyle='-')
    return True



#-------------------------------------------------------------------------------
# Execute:

# err_vs_RR_dt()
# err_vs_RR_dt_mosaic()

sine_plot()
# sine_mosaic()

# uv_corrug(lm=[1,2], domain=False, show=False)
# uv_corrug(lm=[-1,0.5])

# sine_plot(subplot=211)
# err_vs_RR_dt(subplot=212)
# pylab.show()
