# file: ../contrib/JEN/pylab/PyNodeNamedGroups.py

# Author: J.E.Noordam
# 
# Short description:
#   Baseclass for a zoo of PyNode classes.
#   It contains functions that manipulate named groups of values,
#   which are derived from the results of its children.
#   The named groups can be turnrd into other named groups
#   by means of python mathematical expressions, in which the
#   names of the groups serve as variables.
#
# History:
#   - 12 apr 2008: creation (from PyPlot.py)
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
#-------------------------------------------------------------------------------

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

import inspect
import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;


#=====================================================================================
# The PyNodeNamedGroups base class:
#=====================================================================================

class PyNodeNamedGroups (pynode.PyNode):
  """Extract named groups of Vells from its child results."""

  def __init__ (self, *args, **kwargs):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution')
    self._count = -1
    self.extractgroups = record()
    self._namedgroups = record()
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base class for a category of pyNodes.
    It contains functions that manipulate named groups of values,
    which are derived from the results of its children.
    The named groups can be turnrd into other named groups
    by means of python mathematical expressions, in which the
    names of the groups serve as variables.

    First of all, this baseclass contains functions for the
    extraction of named groups from its child results.
    This is specified by attaching a record named 'extractgroups' to
    the constructor, containing zero or more named records:
    .   ns.plot << Meq.PyNode(class_name='PyPlot', module_name=__file__,
    .        extractgroups=record(name1=record(child=... [, vells=...]),
    .                             name2=record(child=... [, vells=...]),
    .                             ...
    .                            ))

    If no extractgroups record has been provided, or if it is empty,
    or if it is not a record, a default record will be assumed:
    .        extractgroups=record(vv=record(child='*', vells=[0]))
    i.e. it will make a single group (named 'vv') from the first vells
    (object) of all its 'extractable' children.

    A group specification record may have the following fields:
    - child = '*'           (default) all children
            = '2/3'         the second third of its chidren (etc)
            = [0,2,7,5,...] any vector of child indices
    - vells = [0]           (default) the first vells of each child result
            = [1,2,2,1,3]   any vector of vells indices
            = None          the group will contain entire result objects
    - vexpr = None          (default) python expression
              'mean()'      initial operation on each vells
    """
    ss = self.attach_help(ss, PyNodeNamedGroups.help.__doc__,
                          classname='PyNodeNamedGroups',
                          level=level, mode=mode)
    return ss

  #...................................................................

  def attach_help(self, ss, s, classname='PyNodeNamedGroups',
                  level=0, mode=None, header=True):
    """
    This is the generic routine that does all the work for .help(). 
    It attaches the given help-string (s, in triple-quotes) to ss.
    The following modes are supported:
    - mode=None: interpreted as the default mode (e.g. 'list').
    - mode='list': ss is a list of strings (lines), to be attached to
    the node state. This is easier to read with the meqbrowser.
    - mode='str': ss is a string, in which lines are separated by \n.
    This is easier for just printing the help-text.
    """
    if mode==None:           # The default mode is specified here
      mode = 'list'
    if mode=='list':  
      if not isinstance(ss,(list,tuple)): ss = []
    else:                    # e.g. mode=='str'
      if not isinstance(ss,str): ss = ''
    sunit = '**'             # prefix unit string

    if header:
      h = sunit+(level*sunit)+'** Help for class: '+str(classname)
      if mode=='list':
        ss.append(h)
      else:
        ss += '\n'+h

    prefix = sunit+(level*sunit)+'   '
    cc = s.split('\n')
    for c in cc:
      if mode=='list':
        ss.append(prefix+c)
      else:
        ss += '\n'+prefix+c
    return ss
    
  #-------------------------------------------------------------------
    
  def update_state (self, mystate):
    """Read information from the pynode state record. This is called
    when the node is first created and a full state record is available.
    But also when state changes, and only a partial state record is
    supplied....
    Instead of the state record, we  receive a clever object (mystate)
    which encapsulates the state record with some additional semantics.
    """

    trace = False
    trace = True

    if True:
      # Attach the help for this class to the state record.
      # It may be read with the browser after building the tree.
      if getattr(self, 'help', None):
        ss = self.help(mode='list')
        mystate('pyplot_node_help',ss)
        if trace:
          print '\n** Help attached to node state record:'
          print '\n** self.help(mode=list):\n'
          for s in ss:
            print s
          print '\n** self.help(mode=str):\n'
          print self.help(mode='str')
          print ' '

    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    print '** self.child_indices =',self.child_indices
    if isinstance(self.child_indices,int):
      self.child_indices = [self.child_indices]
    self._num_children = len(self.child_indices)

    if trace:
      print '\n*******************************************'
      print '** .update_state()',self.class_name,self.name,self.child_indices
      print '*******************************************\n'
    
    # Read the extractgroups record, and check it:
    mystate('extractgroups', None)
    if not isinstance(self.extractgroups, record):
      self.extractgroups = record()               # make sure it is a record
    if len(self.extractgroups)==0:
      self.extractgroups = record(vv=record())    # at least one group (named vv)
    for key in self.extractgroups.keys():
      rr = self.extractgroups[key]
      if not isinstance(rr, record):
        rr = record()                           # make sure it is a record
      rr.key = key                              # attach the key (group name)
      self.extractgroups[key] = self._check_extractgroup_definition(rr)

    # Finished
    return None


  #-------------------------------------------------------------------

  def _check_extractgroup_definition(self, rr, trac=True):
    """Helper function to check the validity of the given definition (rr)
    of an extractgroup (used to extract information from its children).
    Called by .update_state().
    """

    # Deal with the selection of children:
    # NB: String specs are not converted to child index vectors, because this can
    # only be done when the nr of 'used' children is known (see .get_result()).
    rr.setdefault('child','*')                  # default: all
    s = str(rr.key)+': child spec error: '
    if isinstance(rr.child, (list,tuple)):
      pass                                      # assume OK
    elif isinstance(rr.child, str):
      if rr.child=='*':                         # all
        rr.child = range(self.num_children)
      elif '/' in rr.child:                     # e.g. '2/3'
        ss = rr.child.split('/')
        rr.part = int(ss[0])                    # e.g. 2
        rr.nparts = int(ss[1])                  # e.g. 3
      else:
        s += str(rr.child)
        raise ValueError(s)
    else:
      s += str(type(rr.child))
      raise ValueError(s)

    # Deal with the vells specification
    rr.setdefault('vells',[0])                  # default: 1st vells
    s = str(rr.key)+': vells spec error: '
    if isinstance(rr.child, int):               # vells index, e.g. 0
      rr.child = [rr.child]                     # 0 -> [0]
    elif isinstance(rr.child, (list,tuple)):
      pass                                      # assume ok
    elif rr.child==None:                        # extract entire child result(s)
      pass
    else:
      s += str(type(rr.vells))
      raise ValueError(s)

    # Misc
    rr.setdefault('expr',None)                  # python math expression (e.g. mean)
    return rr


  #-------------------------------------------------------------------

  def _extract_groups(self, children, labels, trace=True):
    """Helper function to extract groups of vells from the
    given child-results (children). Called by .get_result().
    """

    import ChildResult
    nc = len(children)

    for key in self.extractgroups.keys():
      rr = self.extractgroups[key]                            # convenience
      iic = self._make_child_selection (nc, rr, trace=False)  # child indices

      # The child result(s) are read by a special object: 
      rv = ChildResult.ResultVector(children, select=iic,
                                    extend_labels=True,
                                    labels=labels)
      if trace:
        rv.display(self.class_name)

      # Make a new namedgroup record (object?):
      ng = record(key=key, child=rr.child, vells=rr.vells,
                  history=[], vv=vv)
      # Attach it:
      self._namedgroups[key] = ng 

    # Finished:
    if trace:
      self.display('_extract_groups()')
    return None
    
      
  #-------------------------------------------------------------------

  def _make_child_selection (self, nc, rr, trace=False):
    """Helper function that returns a list of indices for a subset
    of the nc child nodes.
    """

    # trace = True
    
    iic = []
    if rr.child=='*':
      iic = range(nc)

    elif rr.has_field('part'):
      npp = nc/rr.nparts              # nr per part (should be integer...)
      offset = (rr.part-1)*npp
      for i in range(npp):
        iic.append(i+offset)
    else:
      raise ValueError(rr.child)
        
    if trace:
      print '\n** _make_child_selection(',nc,rr.key,rr.child,') ->',ii,'\n'
    return ii

  #-------------------------------------------------------------------

  def oneliner(self):
    """Helper function to show a one-line summary of this object"""
    ss = '** PyNodeNamedGroups: '
    ss += ' * count='+str(self._count)
    ss += ' * neg='+str(len(self.extractgroups.keys()))
    ss += ' * nng='+str(len(self._namedgroups.keys()))
    return ss
  

  def display (self, txt=None, full=False):
    """Helper function to show the contents of this object
    """
    print '\n'
    print self.oneliner()
    print ' * (',txt,'):'
    print ' *',type(self), self.class_name, self.name
    print ' *',self._num_children, self.child_indices

    print ' * specified extractgroups:'    
    for key in self.extractgroups.keys():
      rr = self.extractgroups[key]
      print '  - '+key+':'+str(rr)

    print ' * total namedgroups:'    
    for key in self._namedgroups.keys():
      rr = self._namedgroups[key]
      print '  - '+key+':'+str(rr)

    print
    return True


  #-------------------------------------------------------------------

  def check_and_append_subplot_not_needed(self, sp, trace=False):
    """Check the integrity of the given subplot definition,
    and append it to self.vellsgroups.subplot.
    """
    trace = True

    # Make sure of some fields:
    sp.setdefault('dxx',None)
    sp.setdefault('dyy',None)

    # Add some fields with statistics:
    import pylab
    yy = pylab.array(sp.yy)
    if len(yy)>0:
      sp.min = yy.min()
      sp.max = yy.max()
      sp.mean = yy.mean()
      sp.stddev = 0.0
      if len(yy)>1:
        if not isinstance(yy[0],complex):
          sp.stddev = yy.stddev()       
    
    if trace:
      self.show_vellsgroup(sp, '.append_subplot()')
      print

    # Append the valid subplot definition:
    if True:
      self.vellsgroups.subplot.append(sp)
    return None


  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Required pyNode function."""

    trace = False
    # trace = True
    
    self._count += 1

    # There are two classes of children:
    # - Those that are derived from PyNodeNamedGroups have a
    #   'namedgroups' field in their result.
    # - The others are 'regular' children whose results are used
    #   to extract results/vells, which are turned into new named groups.
    # Thus, nodes derived from PyNodeNamedGroups may be concatenated
    # to produce complicated results.
    # But they can also be used by themselves.
    
    self._namedgroups = record()  
    cc = []
    for c in children:                             # child results
      if c.has_key('namedgroups'):
        # Copy the existing namedgroup definitions:
        for ng in c['namedgroups'].keys():
          self._namedgroups[key] = ng
      else:
        # Append to the list of 'regular' children.
        cc.append(c)
    
    # Extract new namedgroup definitions from its 'regular' children (if any),
    # and append them to the list self._namedgroups:
    if len(cc)>0:
      self._extract_groups(cc, trace=trace)

    # Make an empty result record
    result = meq.result()

    # Always attach the accumulated namedgroups to the result:
    result.namedgroups = self._namedgroups

    # Finished:
    return result


  #-------------------------------------------------------------------
  # Re-implementable functions (for derived classes)
  #-------------------------------------------------------------------

  def check_vellsgroups (self, trace=False):
    """Check the contents of the input self.vellsgroups record.
    Any re-implementation by derived classes should call this one too.
    """

    if trace:
      self.show_vellsgroups('check_vellsgroups() input')

    rr = self.vellsgroups                                # convenience

    # Some node control parameters:
    rr.setdefault('make_plot', True)                  # if True, make the plot
    rr.setdefault('offset', 0.0)                      # offset multiple subplots

    # There must be as many labels as 'value-nodes'
    # (i.e. no labels are needed for x-coordinate nodes etc)
    # If no labels are specified, it is safe to have a list
    # of None-values for all the children....
    rr.setdefault('labels', self._num_children*[None]) 
    if not isinstance(rr['labels'], (list,tuple)):
      rr['labels'] = self._num_children*[None]

    # Overall parameters 
    # These keys are used to transfer fields to the node result:
    self._ovkeys = ['title','xlabel','ylabel']
    self._ovkeys.extend(['xunit','yunit'])

    title = 'PyNodeNamedGroups_'+self.class_name
    title += '_'+str(self._num_children)
    rr.setdefault('title', self.name) 
    rr.setdefault('xlabel', 'child') 
    rr.setdefault('ylabel', 'result') 
    rr.setdefault('xunit', None) 
    rr.setdefault('yunit', None) 
    rr.setdefault('xindex', 0)                      # index of x-coordinate Vells 
    rr.setdefault('yindex', 1)                      # index of y-coordinate Vells  
    rr.setdefault('zindex', 2)                      # index of z-coordinate Vells  

    # Subplot parameters: 
    # These keys are used to transfer information to subplot definitions:
    self._spkeys = ['color','linestyle','marker','markersize']
    self._spkeys.extend(['legend','plot_sigma_bars','annotate'])
    self._spkeys.extend(['plot_circle_mean'])

    rr.setdefault('subplot',[])                     # subplot definitions 
    rr.setdefault('legend', None)                   # subplot legend
    rr.setdefault('color', 'blue')                  # plot color
    rr.setdefault('linestyle', None)                # line style                  
    rr.setdefault('marker', 'o')                    # marker style
    rr.setdefault('markersize', 5)                  # markersize
    rr.setdefault('msmin',2)                        # min marker size (zmin)
    rr.setdefault('msmax',20)                       # max marker size (zmax)
    rr.setdefault('annotate', True)                 # do annotation
    rr.setdefault('plot_sigma_bars', True)          # plot error-bars
    rr.setdefault('plot_circle_mean', False)         # plot circle around (0,0) with radius=mean

    if trace:
      self.show_vellsgroups('check_vellsgroups() checked')
    return None


  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    See .help() for details.
    """
    rr = self.vellsgroups                         # convenience
    # trace = True
    if trace:
      print '\n** .define_subplots():'

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children,
                                  extend_labels=True,
                                  labels=rr.labels)
    if trace:
      rv.display(self.class_name)

    # Create an empty subplot definition record, and initialize it:
    sp = record()
    for key in self._spkeys:
      sp[key] = rr[key]

    # Fill in the data from the child result(s):
    sp.yy = rv.vv()
    sp.dyy = None
    if sp.plot_sigma_bars:
      sp.dyy = rv.dvv()
    sp.xx = rv.xx()
    sp.dxx = None
    sp.labels = rv.labels()

    # Check and append the subplot definition:
    self.check_and_append_subplot(sp, trace=trace)
    if trace:
      self.show_vellsgroups('.define_subplots()')
    return None








#=====================================================================================
#=====================================================================================
#=====================================================================================
# Classes derived from PyNodeNamedGroups:
#=====================================================================================
#=====================================================================================
#=====================================================================================


class PyNodeNamedGroupsTensorVells (PyNodeNamedGroups):
  """Class derived from PyNodeNamedGroups."""

  def __init__ (self, *args, **kwargs):
    PyNodeNamedGroups.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Define one or more subplot record(s).
    Assume that its children are tensor nodes of the same kind,
    i.e. each with the same number of Vells.
    Make separate subplots for each of the Vells.
    Parameters like color, marker, markersize, etc may be lists,
    with different values for each subplot.
    """
    ss = self.attach_help(ss, PyNodeNamedGroupsTensorVells.help.__doc__,
                          classname='PyNodeNamedGroupsTensorVells',
                          level=level, mode=mode)
    return PyNodeNamedGroups.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_vellsgroups (self, trace=False):
    """Check the contents of the input self.vellsgroups record.
    """
    # trace = True

    rr = self.vellsgroups                                # convenience

    rr.setdefault('index', '*')                       # indices of Vells to be plotted
    rr.setdefault('xindex', None)                     # index of x-coord Vells
    rr.setdefault('yindex', None)                     # index of y-coord Vells
    
    # First do the generic checks (mandatory!) 
    PyNodeNamedGroups.check_vellsgroups(self, trace=trace)
    return None


  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.vellsgroups                         # convenience
    # trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children, labels=rr.labels,
                                  extend_labels=False,
                                  xindex=rr.xindex,
                                  yindex=rr.yindex)
    if trace:
      rv.display(self.class_name)

    # The Vells to be plotted are specified by rr.index:
    nvells = rv[0].len()                       # nr of Vells in 1st (!) child
    if rr.index=='*':
      rr.index = range(nvells)      
    elif isinstance(rr.index, int):
      rr.index = [rr.index]

    # Make separate suplot definitions for each Vells:
    for index in rr.index:
      if index<0 or index>=nvells:
        pass                                   # out of range
      elif index==rr.xindex:
        pass                                   # x-coord Vells: ignore
      elif index==rr.yindex:
        pass                                   # y-coord Vells: ignore
      else:
        sp = record()
        for key in self._spkeys:               # transfer standard fields
          sp[key] = self.getval(rr[key], index=index, trace=trace)  
        sp.yy = rv.vv(index=index)
        sp.xx = rv.xx(index=index)
        sp.labels = rv.labels(index=index)
        sp.dyy = None
        sp.dxx = None
        if sp.plot_sigma_bars:
          sp.dyy = rv.dvv(index=index)
          sp.dxx = rv.dxx(index=index)
        self.check_and_append_subplot(sp, trace=trace)

    # Finished:
    if trace:
      self.show_vellsgroups('.define_subplots()')
    return None




#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================


def format_float(v, name=None, n=2):
  """Helper function to format a float for printing"""
  if isinstance(v, complex):
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

#-----------------------------------------------------------

def format_vv (vv):
  if not isinstance(vv,(list,tuple)):
    return str(vv)
  elif len(vv)==0:
    return 'empty'
  import pylab              # must be done here, not above....
  ww = pylab.array(vv)
  # print '\n** ww =',type(ww),ww
  s = '  length='+str(len(ww))
  s += format_float(ww.min(),'  min')
  s += format_float(ww.max(),'  max')
  s += format_float(ww.mean(),'  mean')
  if len(ww)>1:                       
    if not isinstance(ww[0],complex):
      s += format_float(ww.stddev(),'  stddev')
  return s



#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  children = dict()
  rr = dict()
  classnames = dict()

  ftx= ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())
  ft= ns.freqtime << Meq.Add(Meq.Time(),Meq.Freq())
  gsx = ns.cx_gauss << Meq.ToComplex(Meq.GaussNoise(stddev=0.1),
                                     Meq.GaussNoise(stddev=0.1))
  gs = ns.gauss << Meq.GaussNoise(stddev=0.5)

  tfrac = ns.tfrac << Meq.Multiply(Meq.Time(),0.1)
  ffrac = ns.ffrac << Meq.Multiply(Meq.Freq(),0.1)


  #----------------------------------------------------------------------
  
  if False:
    ccx = []
    ccy = []
    ccz = []
    ccxy = []
    ccxyz = []
    labz = []
    labxy = []
    labxyz = []
    yname = 'y1p'
    xname = 'x1p'
    zname = 'z1p'
    vname = 'v1p'
    
    n = 5
    for i in range(n):

      x = ns[xname](i) << (gs + random.gauss(i,0.3))
      ccx.append(x)

      y = ns[yname](i) << (gs + random.gauss(i,0.5))
      ccy.append(y)

      z = ns[zname](i) << (gs + random.gauss(i,0.3))
      ccz.append(z)
      labz.append('z_'+str(i))    

      xy = ns.xy(i) << Meq.Composer(x,y)
      ccxy.append(xy)
      labxy.append('xy_'+str(i))    

      xyz = ns.xyz(i) << Meq.Composer(x,y,z)
      ccxyz.append(xyz)
      labxyz.append('xyz_'+str(i))    

    if 1:
      classname = 'PyPlotXY'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        markersize=10,
                        labels=labxy,
                        plot_sigma_bars=True)
      children[name] = ccxy

      if 1:
        classname = 'PyPlotUV'
        name = classname
        classnames[name] = classname
        rr[name] = rr['PyPlotXY']
        rr[name]['title'] = name
        children[name] = children['PyPlotXY']


    if 0:
      classname = 'PyPlotXXYY'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        markersize=5,
                        color='magenta',
                        plot_sigma_bars=True,
                        labels=labz)
      children[name] = ccx+ccy


    if 0:
      classname = 'PyPlotXYZ'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        color='red',
                        labels=labxyz)
      children[name] = ccxyz

    if 0:
      classname = 'PyPlotXYZZ'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        color='green',
                        labels=labz)
      children[name] = ccxy+ccz

    if 0:
      classname = 'PyPlotXXYYZZ'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        color='yellow',
                        plot_sigma_bars=True,
                        labels=labz)
      children[name] = ccx+ccy+ccz


  #-----------------------------------------------------------------------


  # Make a bookpage with auxiliary info:
  auxpage = Meow.Bookmarks.Page('aux')
  auxpage.add(ftx, viewer="Result Plotter")
  auxpage.add(ft, viewer="Result Plotter")
  auxpage.add(gsx, viewer="Result Plotter")
  auxpage.add(gs, viewer="Result Plotter")
      
  # Make the pynode(s):
  bookpage = Meow.Bookmarks.Page('pynodes')
  pn = []
  for name in rr.keys():
    print '\n** make_pynode: rr[',name,'] =',rr[name],'\n'
    rr[name].make_plot = True
    pynode = ns[name] << Meq.PyNode(children=children[name],
                                    class_name=classnames[name],
                                    vellsgroups=rr[name],
                                    module_name=__file__)
    pn.append(pynode)
    if rr[name].make_plot:
      Meow.Bookmarks.Page(name).add(pynode, viewer="Svg Plotter")
      bookpage.add(pynode, viewer="Svg Plotter")

  # Make a root node:
  if False:
    # Just bundle all into a single root node:
    ns.rootnode << Meq.Composer(*pn)
  else:
    # Concatenation of all PyPlot nodes:
    vellsgroups = record(title='combined', make_plot=True, offset=-2.0)
    ns.rootnode << Meq.PyNode(children=pn,
                              vellsgroups=vellsgroups,
                              class_name='PyPlot',
                              module_name=__file__)
    bookpage.add(ns.rootnode, viewer="Svg Plotter")

  # Finished:
  return True
  


#=====================================================================================
# Execute a test-forest:
#=====================================================================================

def _test_forest (mqs,parent,wait=False):
  from Timba.Meq import meq
  nf2 = 10
  nt2 = 5
  cells = meq.cells(meq.domain(-nf2,nf2,-nt2,nt2),
                    num_freq=2*nf2+1,num_time=2*nt2+1);
  print '\n-- cells =',cells,'\n'
  request = meq.request(cells,rqtype='e1');
  a = mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True


def _tdl_job_sequence (mqs,parent,wait=False):
  from Timba.Meq import meq
  for i in range(5):
    cells = meq.cells(meq.domain(i,i+1,i,i+1),num_freq=20,num_time=10);
    rqid = meq.requestid(i)
    print '\n--',i,rqid,': cells =',cells,'\n'
    request = meq.request(cells, rqid=rqid);
    a = mqs.meq('Node.Execute',record(name='rootnode',request=request), wait=wait)
  return True


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

  # run in batch mode?
  if '-run' in sys.argv:
    from Timba.Apps import meqserver
    from Timba.TDL import Compile
    
    # this starts a kernel.
    mqs = meqserver.default_mqs(wait_init=10);

    # This compiles a script as a TDL module. Any errors will be thrown as
    # an exception, so this always returns successfully. We pass in
    # __file__ so as to compile ourselves.
    (mod,ns,msg) = Compile.compile_file(mqs,__file__);
    
    # this runs the _test_forest job.
    mod._test_forest(mqs,None,wait=True);

  elif True:
    pp = PyPlotXY()
    print pp.help()

  else:
    #  from Timba.Meq import meqds 
    # Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
