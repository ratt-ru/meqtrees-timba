#!/usr/bin/env python

# file: ../contrib/JEN/util/JEN_pylab.py

# JEN_pylab.py
#
# Author: J.E.Noordam
# 
# Short description:
#   Set of subroutines that help to make pylab (mapplotlib) plots 
#
# History:
#    - 14 aug 2006: creation, from pylab_transients.py
#    - 28 aug 2006: plot_ellipse()
#    - 29 oct 2006: copied from LOFAR/Timba/PyApps/src/Trees/JEN_pylab.py
#    - 02 nov 2006: extended plot_xaxis and plot_yaxis
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
# from pylab import *




#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def on_entry(ctrl, funcname='<funcname>',
             save=False, savefile=None,
             xlabel=None, ylabel=None, title=None):
    """Helper function called at the start of plot-routines"""

    ctrl['funcname'] = funcname            # current funcname 
    ctrl.setdefault('nesting', [])
    ctrl.setdefault('called', [])
    ctrl['nesting'].append(funcname)       # current nesting sequence 
    ctrl['called'].append(funcname)        # list of all functions called 
    ctrl.setdefault('level', -1)           # nesting level (depth)
    ctrl['level'] += 1                     # increment 
    ctrl.setdefault('trace', False)        

    ctrl.setdefault('dispose', True)       # if False, inhibit save and/or show
    ctrl.setdefault('show', True)          # if True, show the top-level plot
    ctrl.setdefault('save', save)          # if True, save the top-level plot
    if not isinstance(savefile, str): savefile = funcname
    ctrl.setdefault('savefile', savefile) 
    ss = ctrl['savefile'].split('.')       # check for savefile extension
    if len(ss)==1: ctrl['savefile'] += '.png'

    ctrl.setdefault('figure', None)        # integer: 1,2,3,...
    ctrl.setdefault('subplot', None)       # integer: nrow*100+ncol*10+iplot (all 1-relative)
    ctrl.setdefault('plopos', dict(iplot=1, irow=1, icol=1, nrow=1, ncol=1))

    if not isinstance(title, str): title = funcname
    ctrl.setdefault('title', title)
    ctrl.setdefault('xlabel', xlabel)
    ctrl.setdefault('ylabel', ylabel)
    if not isinstance(ctrl['xlabel'], str): ctrl['xlabel'] = xlabel
    if not isinstance(ctrl['ylabel'], str): ctrl['ylabel'] = ylabel

    ctrl.setdefault('window', dict())      # xmin, ymax etc       
    ctrl.setdefault('tmargin', 0.10)
    ctrl.setdefault('bmargin', 0.05)
    ctrl.setdefault('lmargin', 0.05)
    ctrl.setdefault('rmargin', 0.05)

    ctrl.setdefault('auxinfo', dict())
    ctrl.setdefault('legend', [])
    ctrl.setdefault('rider', dict())

    # Deal with figure (integer) and subplot (integer):
    if ctrl['figure']:
        pylab.figure(ctrl['figure'])
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
        ctrl['dispose'] = False
    # else:
    #   if isinstance(title, str): ctrl['title'] = title

    # Finished. Return the funcname:
    if ctrl['trace']:
        ctrl_display(ctrl,'end of on_entry()')
    return funcname
        
#-------------------------------------------------------------------------------

def on_exit(ctrl, mosaic=False):
    """Helper function called at the end of plot-routines"""

    # ctrl['dispose'] = ctrl['save'] or ctrl['show']

    if not mosaic and ctrl['level']==0:
        # Finish the plot:
        if ctrl['figure']: pylab.figure(ctrl['figure'])
        xlabel = ctrl['xlabel']
        ylabel = ctrl['ylabel']
        title = ctrl['title']
        if not isinstance(xlabel, str): xlabel = '<xlabel>'
        if not isinstance(ylabel, str): ylabel = '<ylabel>'
        if not isinstance(title, str): title = ctrl['funcname']
        if ctrl['subplot']:
            pylab.subplot(ctrl['subplot'])
            # Limit the length of the label strings a bit,
            # depending on the nr of subplots in the figure:
            pp = ctrl['plopos']                            # convenience
            tmax = min(len(title), 80/pp['ncol'])
            xmax = min(len(xlabel), 80/pp['ncol'])
            ymax = min(len(ylabel), 60/pp['nrow'])
            pylab.xlabel(xlabel[:xmax])
            if pp['icol']==1: pylab.ylabel(ylabel[:ymax])
            if pp['irow']==1: pylab.title(title[:tmax])
        else:
            # If only one subplot, use the entire label strings:
            pylab.xlabel(xlabel)
            pylab.ylabel(ylabel)
            pylab.title(title)
        # Set the window (margins etc):
        set_window(ctrl)
        # Show the auxiliary info (if any) in the top-left corner:
        show_auxinfo(ctrl)
        # Make the legend in the top-right corner:
        if len(ctrl['legend'])>0:
            pylab.legend(ctrl['legend'])

    # Dispose of the plot:
    if ctrl['dispose'] and ctrl['level']==0:
        # Save the plot(s) to savefile:
        if ctrl['save']:                 
            savefile = ctrl['savefile']
            pylab.savefig(savefile)
            print '\n** saved plot in file:',savefile,'\n'
            ctrl_display(ctrl,'.on_exit(): saved')
        # Show the plot on the screen:
        if ctrl['show']:          
            # NB: .show() freezes things until released, so do this last:
            ctrl_display(ctrl,'.on_exit(): shown')
            pylab.show()

    # Finished: Decrement nesting level (depth)
    if ctrl['trace']:
        ctrl_display(ctrl,'.on_exit()')
    ctrl['level'] -= 1
    if ctrl['level']>=0:
        ctrl['nesting'] = ctrl['nesting'][:ctrl['level']+1] 
        ctrl['funcname'] = ctrl['nesting'][ctrl['level']] 
    return ctrl

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def ctrl_display(ctrl, txt=None):
    """Helper function to show the contents of the ctrl record"""
    # Make a list of the keys that are always there, in some order:
    keys = ['funcname','level','nesting','called',
            'title','xlabel','ylabel',
            'save','savefile','show','trace',
            'tmargin','bmargin','lmargin','rmargin',
            'figure','subplot','plopos',
            'window','auxinfo','legend','rider']
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
#-------------------------------------------------------------------------------

def adjust_window(ctrl, xx=None, yy=None):
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

def set_window(ctrl):
    """Helper function to set the plot-window"""
    ww = ctrl['window']                                    # convenience       
    ww.setdefault('xmin',-1.0)
    ww.setdefault('xmax',1.0)
    ww.setdefault('ymin',-1.0)
    ww.setdefault('ymax',1.0)

    # Some helper values:
    yspan = ww['ymax'] - ww['ymin']
    xspan = ww['xmax'] - ww['xmin']
    if yspan<=0: yspan = 2.0
    if xspan<=0: xspan = 2.0
 
    # Plot the x and y axes, if appropriate:
    plot_xaxis = False
    plot_yaxis = False
    if ww['ymin']*ww['ymax']<=0: plot_xaxis = True
    if ww['xmin']*ww['xmax']<=0: plot_yaxis = True
    if abs(xspan)>10*abs(ww['xmin']):
        plot_yaxis = True
        ww['xmin'] = 0.0
    elif abs(xspan)>10*abs(ww['xmax']):
        plot_yaxis = True
        ww['xmax'] = 0.0
    if abs(yspan)>10*abs(ww['ymin']):
        plot_xaxis = True
        ww['ymin'] = 0.0
    elif abs(yspan)>10*abs(ww['ymax']):
        plot_xaxis = True
        ww['ymax'] = 0.0

    # Calculate the window coordinates by adding a small margin in all directions:
    ww['wxmin'] = ww['xmin'] - xspan*ctrl['lmargin']
    ww['wxmax'] = ww['xmax'] + xspan*ctrl['rmargin']
    ww['wymin'] = ww['ymin'] - yspan*ctrl['bmargin']
    ww['wymax'] = ww['ymax'] + yspan*ctrl['tmargin']
    ww['wyspan'] = ww['wymax'] - ww['wymin']
    ww['wxspan'] = ww['wxmax'] - ww['wxmin']

    # Perform some pylab functions:
    if ctrl['figure']: pylab.figure(ctrl['figure'])
    if ctrl['subplot']: pylab.subplot(ctrl['subplot'])
    if True:
        # Plot the x and y axes, if appropriate:
        mult = 1.0
        mult = 1.05
        if plot_xaxis:
            pylab.plot([mult*ww['xmin'], mult*ww['xmax']], [0.0,0.0], color='gray')
        if plot_yaxis:
            pylab.plot([0.0,0.0], [mult*ww['ymin'], mult*ww['ymax']], color='gray')
    # NB: Do this LAST (otherwise it makes its own margin....)
    pylab.axis([ww['wxmin'], ww['wxmax'], ww['wymin'], ww['wymax']])

    # Finished: 
    ctrl['window'] = ww                                          # replace
    return True

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def auxinfo(ctrl, name=None, value=None, unit=None, comment=None):
    """Store auxiliary information in named fields of the ctrl['auxinfo'] record.
    This is used by show_auxinfo() to write lines on the plot."""
    if len(ctrl['nesting'])>1: name = (ctrl['level']*'.')+ctrl['funcname']+'_'+name
    if not ctrl['auxinfo'].has_key(name):                    # first time
        ctrl['auxinfo'][name] = dict(count=1, value=value, unit=unit, comment=comment,
                                     level=ctrl['level'], funcname=ctrl['funcname'])
    else:                                                    # multiple
        rr = ctrl['auxinfo'][name]                           # convenience
        if rr['count']==1: rr['value'] = [rr['value']]       # start a list 
        rr['value'].append(value) 
        rr['count'] += 1                                     # increment
        ctrl['auxinfo'][name] = rr                           # replace
    return True

#-------------------------------------------------------------------------------

def show_auxinfo(ctrl):
    """Helper function to construct lines of auxiliary information
    from the fields of the ctrl['auxinfo'] record,
    and write them into the top left corner of the current (sub)plot"""
    ww = ctrl['window']                                          # convenience
    pp = ctrl['plopos']                                          # convenience
    dy = ww['wyspan']/20
    dx = ww['wxspan']/10
    y = ww['wymax']-2*dy
    if ctrl['figure']: pylab.figure(ctrl['figure'])
    if ctrl['subplot']:
        y = ww['wymax']-dy
        dx /= 2 
        pylab.subplot(ctrl['subplot'])                           # e.g. 211,212,...?
        if pp['nrow']==2: dy = ww['wyspan']/15                   # two rows of subplots
        if pp['nrow']==3: dy = ww['wyspan']/10                   # three rows

    # Write the lines of auxinfo to the (sub)plot:
    for key in ctrl['auxinfo'].keys():
        rr = ctrl['auxinfo'][key]
        s = key
        if rr['count']==1:                                       # single call 
            if not rr['value']==None:
                s += ' = '+str(rr['value'])
        else:                                                    # multiple calls
            # Condense the information from multiple calls:
            v = rr['value']
            same = True
            count = len(v)
            for i in range(1,count):
                if not v[i]==v[0]: same = False
            if same:
                s += ' = ('+str(count)+'x)'+str(v[0])
            else:
                s += ' = ('+str(count)+')'+str(v)
        # Deal with a python bug that turns 0.1 into 0.1000000000001 etc...
        for k in range(15,6,-1):
            s = s.replace(k*'0','00')
            s = s.replace(k*'9','00')
        # Attach extra info to the line:
        if isinstance(rr['unit'], str): s += ' '+rr['unit']
        if isinstance(rr['comment'], str): s += '  ('+rr['comment']+')'
        # Write the auxinfo line:
        y -= dy
        pylab.text(ww['wxmin']+dx,y, str(s), color='gray')
    return True



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def plot_line (ctrl, xx=[0,1], yy=[0,1], color='red',
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
    if len(yy)==1:
        xx = [min(xx),max(xx)]
        yy = [yy[0],yy[0]]
    elif len(xx)==1:
        yy = [min(yy),max(yy)]
        xx = [xx[0],xx[0]]
    adjust_window(ctrl, xx=xx, yy=yy)
    if style=='dashed': style='--'   
    if style=='solid': style='-'
    if style=='dotted': style=':'
    if style=='dashdot': style='-.'
    if ctrl['figure']:
        pylab.figure(ctrl['figure'])
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    pylab.plot(xx, yy, linestyle=style, linewidth=width, color=color)

    # If a label is supplied (string), deal with it:
    pp = ctrl['plopos']                                # convenience
    if isinstance(label, str):
        valign = 'center'
        n = len(xx)-1
        if isinstance(labelpos, bool):                 # labelpos = True/False
            labelpos = 'start'
        if not isinstance(labelpos, str):              # labelpos = None
            ctrl['legend'].append(label)                 
        elif labelpos=='start':                        
            halign = 'right'                           # to the left(!) of the start-point
            if len(label)<15:
                ctrl['lmargin'] = 0.1*(1+pp['ncol'])
            else:
                valign = 'bottom'
                halign = 'left'                        # to the right(!) of the start-point
            pylab.text(xx[0], yy[0], label+' .', color=color,
                       fontsize=12,
                       horizontalalignment=halign,    
                       verticalalignment=valign)      
        elif labelpos=='end':
            halign = 'left'                            # to the right(!) of the end-point
            if len(label)<15:
                ctrl['rmargin'] = 0.1*(1+pp['ncol'])
            else:
                valign = 'bottom'
                halign = 'right'                       # to the left(!) of the end-point
            pylab.text(xx[n], yy[n], '. '+label, color=color,
                       fontsize=12,
                       horizontalalignment=halign,    
                       verticalalignment=valign)      
    return True


#-------------------------------------------------------------------------------

def plot_marker (ctrl, xx=0.5, yy=0.5, color='blue',
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
    if ctrl['figure']:
        pylab.figure(ctrl['figure'])
    if ctrl['subplot']:
        pylab.subplot(ctrl['subplot'])
    # The label can be a string or a list of strings (or Nones, which are ignored).
    if not label==None:
        if not isinstance(label, (list,tuple)): label=[label]
    # NB: The default is 'bottom' and 'left', which actually places the label
    #     at the top-right position of the marker......!!!
    # The position of the label w.r.t to the marker:
    halign = 'left'                                      # left, right, center 
    valign = 'bottom'                                    # bottom, top, center
    # The position may be specified via labelpos:
    if isinstance(labelpos, str):                        # e.g. ['top right']
        ss = labelpos.split(' ')
        if len(ss)>1:
            valign = ss[0] 
            halign = ss[1]
        elif labelpos in ['left','right','center']:
            halign = labelpos
        elif labelpos in ['bottom','top','center']:
            valign = labelpos
        print label,': labelpos =',labelpos,':',halign,valign

    # OK, make the markers and their labels:
    pp = ctrl['plopos']                                  # convenience
    for i in range(len(xx)):
        # pylab.semilogy([xx[i]], [yy[i]], marker=style, # needs some thought...
        pylab.plot([xx[i]], [yy[i]], marker=style,
                   markerfacecolor=color, markersize=size,
                   markeredgecolor=color, markeredgewidth=1)
        if (not label==None) and i<len(label) and (not label[i]==None):
            lstr = '. '+str(label[i])
            if halign=='right': lstr = str(label[i])+' .'
            if len(label[i])>5:
                if halign=='right': ctrl['lmargin'] = 0.1*(1+pp['ncol'])
                if halign=='left': ctrl['rmargin'] = 0.1*(1+pp['ncol'])
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

def rider(ctrl, item=None, append=None, trace=True):
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
#--------------------------------------------------------------------------------

def plot_ellipse(x=0, y=0, a=1, b=None, angle=0, mult=[1.0],
                 pmin=0.0, pmax=2*pylab.pi, dp=0.1, 
                 color='blue', style='-', width=1, label=None,
                 show_center=False, show_spokes=False, 
                 show_args=False, **ctrl):
    """Plot ellipse(s) with centre at (x,y) and axis-ratio a/b.
    - If b is not specified, a circle will be drawn (b=a).
    - If mult is a list, concentric ellipses will be drawn.
    - The ellipse(s) may be rotated with angle (rad) around centre (x,y).
    - An arc between (pmin,pmax) rad may be specified, and an interval dp."""

    funcname = on_entry(ctrl, 'plot_ellipse')

    # Pylab requires floats:
    x = float(x)
    y = float(y)
    angle = float(angle)

    # Cirle or ellipse
    if b==None: b = a                                      # b=a: circle

    if show_args:
        auxinfo(ctrl, 'a', a)
        if len(mult)>1 or not mult[0]==1.0:
            auxinfo(ctrl, 'mult', mult)
        auxinfo(ctrl, 'axis-ratio', b/a)

    # Determine the number of radial spokes:
    pmax = float(pmax)
    pmin = float(pmin)
    pmax = max(pmax,pmin)
    dp = abs(dp)
    if dp>(pmax-pmin): dp = (pmax-pmin)
    if dp>1.0: dp = 1.0                                    # ....?
    segment = not (pmin==0.0 and pmax==2*pylab.pi)         # if True, not fully closed
    if segment:
        pp = pylab.arange(pmin,pmax,dp*0.999999)
        pp[len(pp)-1] = pmax
    else:
        pp = pylab.arange(pmin,pmax+dp,dp*0.999999)

    if show_args:
        if segment:
            auxinfo(ctrl, 'pmin', pmin, 'rad')
            auxinfo(ctrl, 'pmax', pmax, 'rad')
        if not dp==0.1: auxinfo(ctrl, 'dp', dp, 'rad')
        if not angle==0.0: auxinfo(ctrl, 'angle', angle, 'rad')

    # Draw two or more concentric ellipses, with axis ratio a/b
    # The axes are multiplied with the factors in mult.
    for i in range(len(mult)):
        first = (i==0)
        last = (i==len(mult)-1)
        xx = []
        yy = []
        for p in pp:
            xx.append(x+mult[i]*a*pylab.cos(p))
            yy.append(y+mult[i]*b*pylab.sin(p))
        # Rotate the ellipse by angle around its centre (x,y):
        rr = _rotate(xx, yy, angle=angle, x=x, y=y)
        line_style = style
        line_width = width
        if not (first or last): line_width = 1
        plot_line(ctrl, rr['xx'], rr['yy'],
                  color=color, style=line_style, width=line_width)
        if first:
            # Coordinates of the innermost ellipse:
            xx1 = copy.deepcopy(rr['xx'])
            yy1 = copy.deepcopy(rr['yy'])
        # Coordinates of the outermost ellipse:
        xx2 = copy.deepcopy(rr['xx'])
        yy2 = copy.deepcopy(rr['yy'])
        if label and last:
            plot_marker(ctrl, xx2[0], yy2[0], color=color,
                        label=label, style='dot')

    # Mark the common centre of the ellipse(s):
    if show_center:
        plot_marker(ctrl, x, y, color=color, style='+', size=30)

    if segment or show_spokes:
        # Draw the radial end-spokes of the ellipse segment.
        n = len(xx)-1
        ii = [0,n]
        if show_spokes: ii = range(len(xx))
        if len(mult)==1:
            for i in ii:
                xx1[i] = x
                yy1[i] = y
        for i in ii:
            first = (i==0)
            last = (i==n)
            spoke_style = style
            spoke_width = width
            if not (first or last): spoke_width = 1
            plot_line(ctrl, [xx1[i],xx2[i]], [yy1[i],yy2[i]],
                      color=color, style=spoke_style, width=spoke_width)
        if False:
            plot_marker(ctrl, xx2[0], yy2[0], color='red',
                        label='pp[0]='+str(pp[0]))
            plot_marker(ctrl, xx2[n], yy2[n], color='magenta',
                        label='pp[n]='+str(pp[n]))

    # Finished:
    return on_exit(ctrl)

#-------------------------------------------------------------------------------

def _rotate(xx, yy, angle=0.0, x=0.0, y=0.0):
    """Rotate the given curve (xx,yy) around the point (x,y),
    in anti-clockwise direction.
    The result is returned in a dict (rr) with fields xx and yy."""
    # Make sure that xx and yy are arrays (ALWAYS)
    rr = dict(xx=pylab.array(xx), yy=pylab.array(yy))
    if not angle==0.0:
        sin_angle = pylab.sin(angle)
        cos_angle = pylab.cos(angle)
        if not x==0.0: rr['xx'] -= x
        if not y==0.0: rr['yy'] -= y
        x2 = rr['xx']*cos_angle - rr['yy']*sin_angle
        rr['yy'] = rr['yy']*cos_angle + rr['xx']*sin_angle
        rr['xx'] = x2
        if not x==0.0: rr['xx'] += x
        if not y==0.0: rr['yy'] += y
    return rr

#..............................................................................

def test_rotate(**ctrl):
    funcname = on_entry(ctrl, 'test_rotate()')
    xx = pylab.arange(-5,7,0.1)
    yy = pylab.cos(xx)
    plot_line(ctrl, xx, yy, label='init')
    rr = dict(xx=xx, yy=yy)
    for i in range(3):
        rr = _rotate(rr['xx'], rr['yy'], 0.1)
        plot_line(ctrl, rr['xx'], rr['yy'], color='blue')
    plot_line(ctrl, xx, yy, color='green', style='--', width=3)
    return on_exit(ctrl)
    


#===============================================================================
#===============================================================================
# Test-routines:
#===============================================================================
#===============================================================================

def sine_plot(a1=1, a2=0.5, P1=1.0, P2=4, phoff=0.2,
              show_args=False, **ctrl):
    """Illustrate the feasability of sine-interpolation"""
    funcname = on_entry(ctrl, 'sine_plot',
                        savefile='test_sine_plot',
                        xlabel='v-coordinate',
                        ylabel='source contribution (corrugation)',
                        title='sampling visibility corrugations')
    if show_args:
        auxinfo(ctrl, 'a1', a1, 'slugs')
        auxinfo(ctrl, 'a2', a2, 's')
        auxinfo(ctrl, 'P1', P1, comment='comment')
        auxinfo(ctrl, 'P2', P2)
        auxinfo(ctrl, 'phoff', phoff)
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

    if True:
        ctrl = plot_ellipse(x=1, y=1, a=1, b=2,
                            pmin=1,
                            color='red', style='--', width=2,
                            **ctrl)

    if True:
        ctrl = subsin(a1=15, show_args=show_args, **ctrl)
        ctrl = subsin(P1=5, show_args=show_args, **ctrl)

    return on_exit(ctrl)

#---------------------------------------------------------------------------------

def subsin(a1=4.0, P1=1.5,
           show_args=False, **ctrl):
    """Test function, called in sine_plot()"""
    funcname = on_entry(ctrl, 'subsin',
                        xlabel='x',
                        ylabel='y',
                        title='test')
    if show_args:
        auxinfo(ctrl, 'a1', a1)
        auxinfo(ctrl, 'P1', P1)
    xx = pylab.arange(-2, 10, 0.1)
    plot_line(ctrl, xx, a1*pylab.sin(xx/P1), color='green', labelpos='start',
              label='subsin')
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
    # from numpy import *
    # from num-array.linear_algebra import *
    # from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record

    if 1:
        ctrl = sine_plot(show_args=True, save=True)

    if 0:
        ctrl = sine_mosaic()

    if 0:
        test_rotate()

    if 0:
        ctrl = plot_ellipse(x=1, y=1, a=1.1, b=3,
                            mult = range(4),
                            angle=0.0,
                            pmin=1, 
                            subplot=121, 
                            color='blue', style='-', width=1)
        ctrl = plot_ellipse(x=1, y=1, a=1.1, b=3,
                            mult = [1,2,3,4,5,6],
                            # angle=pylab.pi/4,
                            angle=0.5,
                            subplot=122,
                            label='the rain in spain',
                            show_args=True, show_spokes=True,
                            color='green', style='-', width=2)
        pylab.show()
        
    if 1:
        ctrl_display(ctrl, 'final')


#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


