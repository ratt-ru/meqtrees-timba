#!/usr/bin/env python

# file: ../PyApps/src/Trees/JEN_pylab.py

# JEN_pylab.py
#
# Author: J.E.Noordam
# 
# Short description:
#   Set of subroutines that help to make pylab (mapplotlib) plots 
#
# History:
#    - 14 aug 2006: creation, from pylab_transients.py
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
# from pylab import *




#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def on_entry(ctrl=dict(), funcname='<funcname>',
             xlabel='<xlabel>', ylabel='<ylabel>', title=None):
    """Helper function called at the start of plot-routines"""

    ctrl.setdefault('sequence', [])
    ctrl['sequence'].append(funcname)      # name of current function 
    ctrl.setdefault('level', -1)           # nesting level (depth)
    ctrl['level'] += 1                     # increment
    ctrl['funcname'] = ctrl['sequence'][ctrl['level']] 

    ctrl.setdefault('trace', False)
    ctrl.setdefault('show', True)
    ctrl.setdefault('subplot', None)       # integer: nrow*100+ncol*10+iplot (all 1-relative)
    ctrl.setdefault('plopos', dict(iplot=1, irow=1, icol=1, nrow=1, ncol=1))
    ctrl.setdefault('figure', None) 
    ctrl.setdefault('save', True)
    ctrl.setdefault('savefile', funcname+'.png')
    ctrl.setdefault('rider', dict())
    ctrl.setdefault('auxinfo', [])
    ctrl.setdefault('legend', [])
    ctrl.setdefault('window', dict())      # xmin, ymax etc       
    ctrl.setdefault('tmargin', 0.10)
    ctrl.setdefault('bmargin', 0.05)
    ctrl.setdefault('lmargin', 0.05)
    ctrl.setdefault('rmargin', 0.05)
    ctrl.setdefault('xlabel', xlabel)
    ctrl.setdefault('ylabel', ylabel)
    ctrl.setdefault('title', funcname)

    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])     # set subplot
        k = ctrl['subplot']
        pp = ctrl['plopos']                # convenience
        pp['nrow'] = k/100
        pp['ncol'] = (k-100*pp['nrow'])/10
        pp['iplot'] = k-100*pp['nrow']-10*pp['ncol']
        pp['irow'] = 1+(pp['iplot']-1)/pp['ncol'] 
        pp['icol'] = pp['iplot']-pp['ncol']*(pp['irow']-1)
        ctrl['plopos'] = pp                # re-attach
        ctrl['save'] = False
        ctrl['show'] = False
    else:
        if isinstance(title, str): ctrl['title'] = title
    if ctrl['trace']:
        ctrl_display(ctrl,'end of on_entry()')
    return funcname
        
#-------------------------------------------------------------------------------

def on_exit(ctrl=dict(), mosaic=False):
    """Helper function called at the end of plot-routines"""

    if not mosaic and ctrl['level']==0:
        # Finish the plot:
        if ctrl['subplot']:
            pp = ctrl['plopos']               # convenience
            pylab.subplot(ctrl['subplot'])
            tmax = min(len(ctrl['title']), 80/pp['ncol'])
            xmax = min(len(ctrl['xlabel']), 80/pp['ncol'])
            ymax = min(len(ctrl['ylabel']), 60/pp['nrow'])
            pylab.xlabel(ctrl['xlabel'][:xmax])
            if pp['icol']==1: pylab.ylabel(ctrl['ylabel'][:ymax])
            if pp['irow']==1: pylab.title(ctrl['title'][:tmax])
        else:
            pylab.xlabel(ctrl['xlabel'])
            pylab.ylabel(ctrl['ylabel'])
            pylab.title(ctrl['title'])
        set_window(ctrl)
        show_auxinfo(ctrl)
        if len(ctrl['legend'])>0:
            pylab.legend(ctrl['legend'])
        if not ctrl['trace']:                 # temporary
            ctrl_display(ctrl,'.on_exit()')

    if ctrl['level']==0:
        # Dispose of the plot:
        if ctrl['save']:                 
            savefile = ctrl['savefile']
            pylab.savefig(savefile)
            print '\n** saved plot in file:',savefile,'\n'
            ctrl_display(ctrl,'.on_exit(): saved')
        if ctrl['show']:          
            # NB: .show() freezes things until released, so do this last:
            ctrl_display(ctrl,'.on_exit(): shown')
            pylab.show()

    # Finished: Decrement nesting level (depth)
    if True or ctrl['trace']:
        ctrl_display(ctrl,'.on_exit()')
    ctrl['level'] -= 1
    if ctrl['level']>=0:
        ctrl['funcname'] = ctrl['sequence'][ctrl['level']] 
    return ctrl

#-------------------------------------------------------------------------------

def ctrl_display(ctrl, txt=None):
    """Helper function to show the contents of the ctrl record"""
    # Make a list of the keys that are always there, in some order:
    keys = ['funcname','level','sequence',
            'title','xlabel','ylabel',
            'save','savefile','show','trace',
            'window','tmargin','bmargin','lmargin','rmargin',
            'figure','subplot','plopos',
            'auxinfo','legend','rider']
    # Add the optional keys, and any forgotten ones:
    for key in ctrl.keys():
        if not keys.__contains__(key):
            keys.append(key)
    # Display the fields of ctrl:
    print '\n** JEN_pylab ctrl record:',ctrl['funcname'],'(',txt,')'
    for key in keys:
        print '-',key,'=',ctrl[key]
    print '**\n'
    return True

#-------------------------------------------------------------------------------

def set_window(ctrl):
    """Helper function to set the plot-window"""
    ww = ctrl['window']                    # convenience       
    ww.setdefault('xmin',-1.0)
    ww.setdefault('xmax',1.0)
    ww.setdefault('ymin',-1.0)
    ww.setdefault('ymax',1.0)

    if True:
        # Make sure of the correct order:
        if ww['xmax']<ww['xmin']:
            xmin = ww['xmax']
            ww['xmax'] = ww['xmin']
            ww['xmin'] = xmin
        if ww['ymax']<ww['ymin']:
            ymin = ww['ymax']
            ww['ymax'] = ww['ymin']
            ww['ymin'] = ymin
    if True:
        # Make a small margin in all directions:
        yspan = ww['ymax']-ww['ymin']
        xspan = ww['xmax']-ww['xmin']
        if yspan<=0: yspan = 2.0
        if xspan<=0: xspan = 2.0
        ww['xmin'] -= xspan*ctrl['lmargin']
        ww['xmax'] += xspan*ctrl['rmargin']
        ww['ymin'] -= yspan*ctrl['bmargin']
        ww['ymax'] += yspan*ctrl['tmargin']
    ww['yspan'] = ww['ymax']-ww['ymin']
    ww['xspan'] = ww['xmax']-ww['xmin']

    # Perform some pylab functions:
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    if True:
        # Plot the x and y axes, if appropriate:
        if ww['xmin']*ww['xmax']<0:
            pylab.plot([ww['xmin'], ww['xmax']], [0.0,0.0], color='gray')
        if ww['ymin']*ww['ymax']<0:
            pylab.plot([0.0,0.0], [ww['ymin'], ww['ymax']], color='gray')
    # NB: Do this LAST (otherwise it makes its own margin....)
    pylab.axis([ww['xmin'], ww['xmax'], ww['ymin'], ww['ymax']])

    # Finished: 
    ctrl['window'] = ww             # replace
    return True

#-------------------------------------------------------------------------------

def show_auxinfo(ctrl):
    """Helper function to put some lines (ss) of auxiliary information
    into the top left corner of the current plot"""
    ww = ctrl['window']                                          # convenience
    pp = ctrl['plopos']                                          # convenience
    dy = ww['yspan']/20
    dx = ww['xspan']/10
    y = ww['ymax']-2*dy
    if ctrl['subplot']:
        y = ww['ymax']-dy
        dx /= 2 
        pylab.subplot(ctrl['subplot'])                           # e.g. 211,212,...?
        if pp['nrow']==2: dy = ww['yspan']/15                    # two rows of subplots
        if pp['nrow']==3: dy = ww['yspan']/10                    # three rows
    for s in ctrl['auxinfo']:
        y -= dy
        pylab.text(ww['xmin']+dx,y, str(s), color='gray')
    return True

#-------------------------------------------------------------------------------

def auxinfo(ctrl=dict(), name=None, value=None, unit=None):
    """Append a line to the ctrl[auxinfo] list, for display"""
    s = name
    if not value==None: s += ' = '+str(value)
    if isinstance(unit, str): s += '  ('+unit+')'
    ctrl['auxinfo'].append(s)
    return True

#-------------------------------------------------------------------------------

def adjust_window(ctrl=dict(), xx=None, yy=None):
    """Helper function to adjust the (xy) window in ctrl-record"""
    ww = ctrl['window']
    if not xx==None:
        ww.setdefault('xmin', xx[0])
        ww.setdefault('xmax', xx[0])
        xx1 = pylab.array(xx)
        ww['xmin'] = min(ww['xmin'], min(xx1))
        ww['xmax'] = max(ww['xmax'], max(xx1))
    if not yy==None:
        ww.setdefault('ymin', yy[0])
        ww.setdefault('ymax', yy[0])
        yy1 = pylab.array(yy)
        ww['ymin'] = min(ww['ymin'], min(yy1))
        ww['ymax'] = max(ww['ymax'], max(yy1))
    ctrl['window'] = ww
    return True

#-------------------------------------------------------------------------------

def plot_line (ctrl=dict(), xx=[0,1], yy=[0,1], color='red',
               style='-', width=1, label=None, labelpos=None):
    """Plot a line through the points given by lists/arrays xx and yy,
    using the given color, line-style and line-width.
    - In addition to the regular pylab line-styles, the following are also
      recognised: 'solid', 'dashed', 'dotted', 'dashdot'.
    - If label is a string, the line will be labelled at position labelpos.
      (If label is boolean (e.g. True), labelpos will be converted to 'start'.)
    - If labelpos is not given, the label will be part of the plot-legend.
    - Otherwise, labelpos can be 'start' or 'end'.
    - If labelpos is 'end', the right margin will be extended a bit.
    Do some bookkeeping, like updating the extreme values for the plot."""
    # if not isinstance(xx, (list,tuple,type(pylab.array(0)))): return False
    # if not isinstance(yy, (list,tuple,type(pylab.array(0)))): return False
    adjust_window(ctrl, xx=xx, yy=yy)
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
    """Plot marker(s) at the points given by numbers/lists/arrays xx and yy,
    using the given color, point-style and point-width.
    - If label is a string/list, the marker will be labelled at position labelpos.
      NB: The list may also contain None-items, which will be ignored.
      NB: The list may be shorter than the nr of markers.
    Do some bookkeeping, like updating the extreme values for the plot."""
    if not isinstance(xx, (list,tuple,type(pylab.array(0)))): xx = [xx]
    if not isinstance(yy, (list,tuple,type(pylab.array(0)))): yy = [yy]
    # if not len(xx)==len(yy): return False
    adjust_window(ctrl, xx=xx, yy=yy)
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    # The label can be a string or a list of strings (or Nones, which are ignored).
    if not label==None:
        if not isinstance(label, (list,tuple)): label=[label]
    # NB: The default is 'bottom' and 'left', which actually places the label
    # at the top-right position of the marker...!
    # The position of the label w.r.t to the marker:
    halign = 'left'                                      # left, right, center 
    valign = 'bottom'                                    # bottom, top, center
    # The position may be specified via labelpos:
    if isinstance(labelpos, str):                        # e.g. ['top right']
        ss = labelpos.split(' ')
        valign = ss[0] 
        halign = ss[1]
    # OK, make the markers and their labels:
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

#------------------------------------------------------------------------------------

def draw_ellipse(x=0, y=0, a=1, b=None, pmin=0, pmax=None, dp=None, color='red'):
    """Draw an ellipse (old version)"""
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

#--------------------------------------------------------------------------------

def plot_ellipse(ctrl, x=0, y=0, a=1, b=None, angle=0,
                 pmin=0, pmax=None, dp=None,
                 color='red', style='-', width=1):
    """Plot an ellipse with centre at (x,y) and half-axes (a,b).
    - If b is not specified, a circle will be drawn (b=a)."""
    x = float(x)
    y = float(y)
    angle = float(angle)

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
    if b==None: b = a                                      # b=a: circle
    if not isinstance(b, (list,tuple)): b = [0.0,b]
    for i in range(len(a)):
        xx = []
        yy = []
        for p in pp:
            xx.append(x+a[i]*pylab.cos(p))
            yy.append(y+b[i]*pylab.sin(p))
            plot_line(ctrl, xx, yy, color=color, style=style, width=width)
            plot_marker(ctrl, x, y, color=color, style='+', size=1)
        xx2 = xx
        yy2 = yy
        if i==0:
            xx1 = xx
            yy1 = yy
    if not closed:
        n = len(xx)-1
        plot_line(ctrl, [xx1[0],xx2[0]], [yy1[0],yy2[0]],
                  color=color, style='-',
                  labelpos=None, label=None)
        plot_line(ctrl, [xx1[n],xx2[n]], [yy1[n],yy2[n]], color=color, style='-',
                  labelpos=None, label=None)

    # Finished:
    return True





#===============================================================================
#===============================================================================
# Test-routines:
#===============================================================================
#===============================================================================

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

    if True:
        plot_ellipse(ctrl, x=1, y=1, a=1, b=2,
                     pmin=1, pmax=None, dp=None,
                     color='red', style='--', width=2)

    if True:
        ctrl = subsin(a1=15, **ctrl)
        ctrl = subsin(P1=5, **ctrl)

    return on_exit(ctrl)


#---------------------------------------------------------------------------------

def subsin(a1=4.0, P1=1.5, **ctrl):
    """Test function"""
    funcname = on_entry(ctrl, 'subsin',
                        xlabel='x',
                        ylabel='y',
                        title='test')
    # ctrl_display(ctrl, 'after on_entry() in subsin()')
    # a1 = 4.0
    # P1 = 1.5
    xx = pylab.arange(-2, 10, 0.1)
    plot_line(ctrl, xx, a1*pylab.sin(xx/P1), color='green', labelpos='start',
              label='subsin')
    auxinfo(ctrl, 'subsin', 1.89)
    # ctrl_display(ctrl, 'before on_exit() in subsin()')
    return on_exit(ctrl)


#-------------------------------------------------------------------------------

def sine_mosaic(**ctrl):
    funcname = on_entry(ctrl, 'sine_mosaic')
    sine_plot(subplot=321)
    sine_plot(subplot=322)
    sine_plot(subplot=323)
    sine_plot(subplot=324)
    sine_plot(subplot=325)
    return on_exit(ctrl, mosaic=True)


#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: JEN_pylab.py:\n'
    # from numarray import *
    # from numarray.linear_algebra import *
    # from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record

    if 1:
        ctrl = sine_plot()
        # ctrl_display(ctrl, 'final')

    if 0:
        ctrl = sine_mosaic()


#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


