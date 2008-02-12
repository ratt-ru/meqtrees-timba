#!/usr/bin/env python

# file: ../contrib/JEN/pylab/ChildResult.py

# Author: J.E.Noordam
# 
# Short description:
#   Helps to unpack a child (node) result, for use in pyNodes
#
# History:
#    - 06 feb 2008: creation
#
# Remarks:
#
# Description:
#
#-------------------------------------------------------------------------------

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

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq

import inspect
import random


Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='test_pynode');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;



#=====================================================================================
# Classes:
#=====================================================================================


class Result (object):
  """Helps to unpack a child (node) result"""

  def __init__ (self, result, request=None):

    self._result = result
    self._request = request

    self._Cells = None
    if result.has_key('cells'):
      self._Cells = Cells(result['cells'])  # Cells object!

    self._Vells = dict()             
    self._order = []             
    for i,vellset in enumerate(result['vellsets']):
      key = str(i)
      self._order.append(key)
      self._Vells[key] = Vells(vellset['value'], self._Cells)
      if vellset.has_key('shape'):
        pass
    
    return None

  def len(self):
    """Return the number of (JEN) Vells"""
    return len(self._order)
  def order(self):
    """Return a list of (JEN) Vells keys"""
    return self._order
  def Cells(self):
    """Return its (JEN) Cells object"""
    return len(self._Cells)
                              
  def __getitem__(self, index):
    """Get the specified (index) Vells object. The index may either be
    numeric (0,1,...,.len()-1) or by string (key, from .order())."""
    if isinstance(index,str):
      key = index
    elif isinstance(index, int):
      key = self._order[index]
    return self._Vells[key]

  def oneliner(self):
    """Return a one-line summary of this object""" 
    ss = '** <Result>: '
    ss += ' n='+str(self.len())
    # ss += ' shape='+str(self.shape())
    if self._Cells:
      ss += '   '+self._Cells.oneliner()
    return ss

  def display(self):
    """Print a multi-line summary of this object"""
    print '\n**'
    print ' * ',self.oneliner()
    for key in self._order:
      print '    -',key,':',self._Vells[key].oneliner()
    print '**\n'

  def show (self):
    """Show the MeqResult dict in detail"""
    show_value(self._result)
    return True



#===========================================================
#===========================================================
  
class Vells (object):
  """Helps to hold and unpack a child Vells"""

  def __init__ (self, vells, cells=None):

    self._vells = vells
    self._is_complex = isinstance(self.min(),complex)
    self._shape = list(vells.shape)
    self._len = 1
    for i,k in enumerate(self._shape):
      self._len *= k
    self._cells = cells
    return None

  #-----------------------------------------------------------

  def len (self, expanded=False):
    """Return the nr of cells in the Cells, which may be collapsed.
    If expanded==True, return the nr of cells in the expanded Cells.
    """
    if expanded:
      return self._cells.len()
    return self._len

  def shape (self, expanded=False):
    """Return the shape (list) of the Cells, which may be collapsed.
    If expanded==True, return the shape of the expanded Cells."""
    if expanded:
      return self._cells.shape()
    return self._shape

  def axes (self):
    """Return the axes (list) of the domain."""
    return self._cells.axes()

  def is_complex(self):
    """Return True if the Vells values are complex"""
    return self._is_complex

  def min (self):
    """Return the min value in the cells of the (unexpanded) domain. May be complex."""
    return self._vells.min()

  def max (self):
    """Return the max value of the cells of the (unexpanded) domain. May be complex."""
    return self._vells.max()

  def mean (self):
    """Return the mean over the cells of the (unexpanded) domain. May be complex."""
    return self._vells.mean()

  def stddev (self):
    """Return the stddev over the cells of the (unexpanded) domain"""
    if self._len==1: return 0.0
    if self._is_complex:
      return self._vells.__abs__().stddev()     # not entirely correct: expand first!
    return self._vells.stddev()                 # not entirely correct: expand first!

  def errorbar (self):
    """Return the length of the error-bar (stddev) around the mean.
    If the Vells is complex, complex(stddev,stddev) is returned."""
    stddev = self.stddev()
    if self._is_complex:
      return complex(stddev,stddev)
    return stddev

  #-----------------------------------------------------------

  def oneliner(self):
    ss = '** <Vells>: '
    ss += ' n='+str(self.len())
    ss += ' shape='+str(self.shape())
    if self._is_complex:
      ss += ' (complex)'
    ss += ' min='+format_float(self.min())
    ss += ' max='+format_float(self.max())
    ss += ' mean='+format_float(self.mean())
    ss += ' stddev='+format_float(self.stddev())
    return ss
                              
  def show (self):
    show_value(self._vells)
    return True


#-----------------------------------------------------------
# Helper function:
#-----------------------------------------------------------

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



#===========================================================
#===========================================================

class Cells (object):
  """Helps to interprete a Result Cells"""

  def __init__ (self, cells):

    self._cells = cells

    # Extract the actual list of axes, in the correct order, e.g. ['freq','time']
    axes = list(cells['domain']['axis_map'])
    cs = cells['cell_size']
    self._axes = []
    for i,axis in enumerate(axes):
      axis = str(axis).lower()
      if cs.has_key(axis):
        self._axes.append(axis)

    # Make the correct shape (list):
    self._shape = []
    for key in self._axes:
      self._shape.append(len(cs[key]))

    # Count the number of cells:
    self._len = 1
    for i,k in enumerate(self._shape):
      self._len *= k
      
    return None

  #--------------------------------------

  def len (self):
    """Return the number of cells"""
    return self._len
  
  def shape (self):
    """Return the shape (list) of the cells"""
    return self._shape

  def axes (self):
    """Return the (actual) list of domain axes."""
    return self._axes

  #--------------------------------------

  def oneliner(self):
    ss = '** <Cells>: '
    ss += ' n='+str(self.len())
    ss += ' shape='+str(self.shape())
    ss += ' axes='+str(self._axes)
    return ss
                              
  def show (self):
    show_value(self._cells)
    return True







#=====================================================================================
# Make a pyNode with one child to be unpacked:
#=====================================================================================


class OneChildPyNode (pynode.PyNode):
  """Make a test pyNode that uses the ChildNodeResult class"""

  def __init__ (self, *args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution');
                              
  def get_result (self, request, *children):
    result = children[0]
    # show_value(result)
    cr = Result(result)
    # cr.show()
    # print cr.oneliner()
    cr.display()
    for key in cr.order():
      print cr[key].oneliner()
    return result




#=====================================================================================
# Helper function:
#=====================================================================================

def show_value(v, name=None, level=0, count=None, dirs=True):
  """Helper function"""
  if level==0:
    print '\n\n\n******************************************'
    print type(v)
    if dirs: print '\n',dir(v),'\n'
    count = dict(dirs=dirs)
  prefix = level*'..'

  if isinstance(v, Timba.dmi.MeqCells):
    print prefix,name,type(v)
    print prefix,'- .keys()=',v.keys()
    if not count.has_key('MeqCells'):
      count['MeqCells'] = 1
      if count['dirs']: print '\n** dir(',type(v),'):\n',dir(v),'\n'
    for key in v.keys():
      show_value(v[key],str(name)+'['+key+']',level=level+1, count=count)
    
  elif isinstance(v, Timba.dmi.MeqDomain):
    print prefix,name,type(v)
    if not count.has_key('MeqDomain'):
      count['MeqDomain'] = 1
      if count['dirs']: print '\n** dir(',type(v),'):\n',dir(v),'\n'

  elif isinstance(v, Timba.dmi.MeqVellSet):
    print prefix,name,type(v)
    print prefix,'- .keys()=',v.keys()
    if not count.has_key('MeqVellSet'):
      count['MeqVellSet'] = 1
      if count['dirs']: print '\n** dir(',type(v),'):\n',dir(v),'\n'
    for key in v.keys():
      show_value(v[key],str(name)+'['+key+']',level=level+1, count=count)

  elif isinstance(v, Timba.dmi.MeqVells):
    print prefix,name,type(v)
    print prefix,'- .shape=',v.shape,' .rank=',v.rank
    print prefix,'- .nelements()=',v.nelements()
    print prefix,'- .min(),.max(),.mean()=',v.min(),v.max(),v.mean()
    show_value(v[0],str(name)+'[0]',level=level+1, count=count)
    if v.nelements()>1:
      show_value(v[1],str(name)+'[1]',level=level+1, count=count)
    if not count.has_key('MeqVells'):
      count['MeqVells'] = 1
      if count['dirs']: print '\n** dir(',type(v),'):\n',dir(v),'\n'

  elif isinstance(v,dict):
    print prefix,name,type(v),' .keys()=',v.keys()
    for key in v.keys():
      print prefix,'dict (',name,'): key=',key,type(v[key])
      show_value(v[key],'['+key+']',level=level+1, count=count)

  elif isinstance(v,tuple):
    print prefix,name,type(v),' len(v)=',len(v)
    for i,v1 in enumerate(v):
      print prefix,'tuple (',name,'): i=',i,type(v1)
      show_value(v1,'['+str(i)+']',level=level+1, count=count)

  elif isinstance(v,list):
    print prefix,name,type(v),' len(v)=',len(v)
    print prefix,name,'(len=',len(v),') =',v[0],'...'

  elif isinstance(v, Timba.dmi.MeqResult):
    print prefix,name,type(v)
    if not count.has_key('MeqResult'):
      count['MeqResult'] = 1
      if count['dirs']: print '\n** dir(',type(v),'):\n',dir(v),'\n'

  else:
    print prefix,name,'(',type(v),') =',v

  if level==0:
    print '**\n'
    print '** count =',count,'\n'
  return True



#=====================================================================================
# Make a test-forest:
#=====================================================================================


def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""
  cc = []
  
  if 1:
    # c = ns['child'] << 2.2
    # c = ns['child'] << Meq.Time()
    # c = ns['child'] << Meq.Freq()
    # c = ns['child'] << Meq.Add(Meq.Time(),Meq.Freq())
    # c = ns['child'] << Meq.ToComplex(Meq.Time(),Meq.Freq())
    # c = ns['child'] << Meq.Composer(Meq.Time(),3.4)
    if True:
      cc = []
      cc.append(ns['XX'] << 1+1j)
      cc.append(ns['XY'] << -1+1j)
      cc.append(ns['YX'] << -1-1j)
      cc.append(ns['YY'] << 1-1j)
      c = ns['child'] << Meq.Composer(*cc)
      
    classname = "OneChildPyNode"
    ns.pynode << Meq.PyNode(c, class_name=classname, module_name=__file__)
                
  return True
  


#=====================================================================================
# Execute a test-forest:
#=====================================================================================

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=3,num_time=4);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('pynode',request);
  return True


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();
