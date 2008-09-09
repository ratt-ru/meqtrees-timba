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


class ResultVector (object):
  """Contains a vector of child Results"""

  def __init__ (self, results, name=None,
                labels=None, vlabels=None,
                extend_labels=False,
                select=None, index=None,
                xindex=None, yindex=None, 
                offset=0.0):

    self._name = name
    self._offset = offset
    self._vlabels = vlabels
    self._extend_labels = extend_labels
    self._index = index
    self._xindex = xindex
    self._yindex = yindex

    # A subset of the given list of results may be selected:
    if isinstance(select,(list,tuple)):
      self._select = select
    elif isinstance(select,int):
      self._select = [select]
    else:
      self._select = range(len(results))

    # Make a list of Result objects:
    if not isinstance(results,(list,tuple)):
      results = [results]
    self._Result = []
    for i,k in enumerate(self._select):
      label = str(k)
      if isinstance(labels,(list,tuple)):
        label = '?'
        if k>=0 and k<len(labels):
          label = labels[k]
      # print '--- i=',i,' k=',k,' label=',label
      self._Result.append(Result(results[k], name=label, iseq=i,
                                 vlabels=self._vlabels,
                                 extend_labels=self._extend_labels,
                                 xindex=self._xindex,
                                 yindex=self._yindex,
                                 offset=self._offset))

    # Finished:
    return None

  #---------------------------------------------------------------------
  # Access routines:
  #---------------------------------------------------------------------

  def len(self):
    """Return the number of (JEN) Results"""
    return len(self._Result)

  def name(self):
    """Return the name/label of this object"""
    return str(self._name)

  def __getitem__(self, index):
    """Get the specified (index) Result object."""
    return self._Result[index]


  #---------------------------------------------------------------------
  # display:
  #---------------------------------------------------------------------

  def oneliner(self):
    """Return a one-line summary of this object""" 
    ss = '** <ResultVector> '+str(self.name())+':'
    ss += ' nChildren='+str(self.len())
    if not self._vlabels==None:
      ss += ' '+str(self._vlabels)
    if not self._index==None:
      ss += ' index='+str(self._index)
    if not self._xindex==None:
      ss += ' xindex='+str(self._xindex)
    if not self._yindex==None:
      ss += ' yindex='+str(self._yindex)
    if self._offset:
      ss += ' offset='+str(self._offset)
    return ss


  def display(self, txt=None, full=True):
    """Print a multi-line summary of this object"""
    print '\n** (txt='+str(txt)+')'
    print ' * ',self.oneliner()
    for i,rr in enumerate(self._Result):
      print '    -',i,':',rr.oneliner()
    if full:
      print ' * vv =',self.vv()
      print ' * vcx =',self.vcx()
      print ' * dvv =',self.dvv()
      print ' * labels =',self.labels()
      print ' * xx =',self.xx()
      print ' * dxx =',self.dxx()
      print ' * yy =',self.yy()
      print ' * dyy =',self.dyy()
    print '**\n'

  #---------------------------------------------------------------------
  # Return lists of values for its Results
  #---------------------------------------------------------------------

  def vv(self, index=None):
    """Return a list of values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.vv(index=self.getindex(index)))
    return vv

  def getindex(self, index):
    """Helper function to get the correct (vells) index"""
    if isinstance(index,int): return index
    if isinstance(index,(list,tuple)): return index
    return self._index

  def dvv(self, index=None):
    """Return a list of values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.dvv(index=self.getindex(index)))
    return vv

  def vcx(self, index=None):
    """Return a list of complex values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.vcx(index=self.getindex(index)))
    return vv

  def VV(self, index=None):
    """Return a list of straight values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.VV(index=self.getindex(index)))
    return vv

  def yy(self, index=None):
    """Return a list of yy values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.yy(index=self.getindex(index)))
    return vv

  def xx(self, index=None):
    """Return a list of xx values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.xx(index=self.getindex(index)))
    return vv

  def labels(self, index=None):
    """Return a list of labels."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.labels(index=self.getindex(index)))
    return vv

  def dxx(self, index=None):
    """Return a list of dxx values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.dxx(index=self.getindex(index)))
    return vv

  def dyy(self, index=None):
    """Return a list of dyy values."""
    vv = []
    for i,rr in enumerate(self._Result):
      vv.extend(rr.dyy(index=self.getindex(index)))
    return vv

  #---------------------------------------------------------

  def expand(self, ii, index=None):
    """Expand the given list of node-related values
    (e.g. child indices, or node indices) into a list
    with the same length as the nr of nodes/results.
    """
    vv = []
    for i,rr in enumerate(self._Result):
      vv1 = rr.vv(index=self.getindex(index))
      for j,v in enumerate(vv1):
        vv.append(ii[i])
    return vv



#=====================================================================================
#=====================================================================================


class Result (object):
  """Helps to unpack a child (node) result."""

  def __init__ (self, result, name=None, iseq=0,
                vlabels=None,
                extend_labels=False,
                offset=0.0,
                xindex=None, yindex=None,
                request=None):

    self._result = result               # child result (record)
    
    self._name = str(name)              # child label
    self._iseq = iseq                   # child sequence number
    if name==None:                      
      self._name = 'c'+str(iseq)        # default child label
      
    self._vlabels = vlabels             # list of Vells labels, e.g. [XX,XY,YX,YY]....
    self._extend_labels = extend_labels # if True, append [ivells] to labels
    self._xindex = xindex               # index of 'x' Vells (for x,y plotting)
    self._yindex = yindex               # index of 'y' Vells (for x,y,z plotting)
    self._offset = offset               # optional offset to the values vv
    self._request = request

    self._plotinfo = None
    if result.has_key('plotinfo'):
      self._plotinfo = result['plotinfo']       # plot information

    self._Cells = None
    if result.has_key('cells'):
      self._Cells = Cells(result['cells'])      # Cells object!

    # Make a dict of Vells objects: 
    self._Vells = dict()             
    self._order = []             
    for i,vellset in enumerate(result['vellsets']):
      key = str(i)
      if i==self._xindex:
        key = 'x'
      elif i==self._yindex:
        key = 'y'
      elif isinstance(vlabels,(list,tuple)):
        if i<len(vlabels):
          key = vlabels[i]
      self._order.append(key)
      self._Vells[key] = Vells(vellset['value'], self._Cells)
      if vellset.has_key('shape'):
        pass

    # The values (mean/stddev over the domain) of the result
    self._vv_executed = False
    self._vv = []
    self._VV = []                        # straight....
    self._dvv = []
    self._vcx = []                       # complex version

    # The x-coordinates (mean/stddev):
    self._xx = []
    self._dxx = []

    # The y-coordinates (mean/stddev) (if any):
    self._yy = []
    self._dyy = []

    # Finished:
    return None

  #---------------------------------------------------------------------
  # Access routines:
  #---------------------------------------------------------------------

  def len(self):
    """Return the number of (JEN) Vells in this result"""
    return len(self._order)

  def name(self):
    """Return the name/label of this result"""
    return str(self._name)

  def iseq(self):
    """Return the sequence nr of this result"""
    return self._iseq

  def order(self):
    """Return a list of (JEN) Vells keys"""
    return self._order

  def Cells(self):
    """Return its (JEN) Cells object"""
    return self._Cells
                              
  def plotinfo(self):
    """Return its plotinfo record (if any)"""
    return self._plotinfo
                              
  def __getitem__(self, index):
    """Get the specified (index) Vells object. The index may either be
    numeric (0,1,...,.len()-1) or by string (key, from .order())."""
    if isinstance(index,str):
      key = index
    elif isinstance(index, int):
      key = self._order[index]
    return self._Vells[key]

  #---------------------------------------------------------------------
  # display:
  #---------------------------------------------------------------------

  def oneliner(self):
    """Return a one-line summary of this object""" 
    ss = '** <Result> '+str(self.name())+' (iseq='+str(self.iseq())+'):'
    ss += ' nVells='+str(self.len())
    ss += ' '+str(self._order)
    if self._plotinfo:
      ss += ' (has plotinfo record)'
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


  #---------------------------------------------------------------------
  # Functions for extracting numbers from Vells
  #---------------------------------------------------------------------

  def vv(self, index=None):
    """Calculate the various vectors of values, labels and coordinates.
    Return a list of vv values."""
    if not self._vv_executed:
      self._VV = []
      self._vv = []
      self._vcx = []
      self._dvv = []
      self._labels = []
      self._xx = []
      self._yy = []
      self._dxx = []
      self._dyy = []

      for i,key in enumerate(self._order):
        v = self._Vells[key].mean()                   # the mean of the domain values
        dv = self._Vells[key].sigmabar()              # the stddev of the domain values
        if isinstance(dv,complex): dv = abs(dv)       # .....?

        if self._xindex==i:
          # This Vells contains an x-coordinate value
          if isinstance(v,complex): v = abs(v)        # just in case
          self._xx.append(v)
          self._dxx.append(dv)

        elif self._yindex==i:
          # This Vells contains an y-coordinate value
          if isinstance(v,complex): v = abs(v)        # just in case
          self._yy.append(v)
          self._dyy.append(dv)

        else:
          # This Vells contains a value (v):
          if isinstance(v,complex):
            self._vcx.append(v)                       # complex value
            self._vv.append(v.imag+self._offset)
            self._xx.append(v.real)
            self._dxx.append(dv)
          else:
            self._vv.append(v+self._offset)
            self._vcx.append(complex(v+self._offset,0.0))
          self._VV.append(v+self._offset)
          self._dvv.append(dv)
          
          label = self.name()
          if self._extend_labels:
            if not isinstance(self._vlabels,(list,tuple)):    # Vells labels
              if len(self._order)>1:
                label += '['+str(key)+']'
            elif i>=len(self._vlabels):                   # too few vlabels
              label += '['+str(key)+'?]'
            elif len(self._order)>1:
              label += '['+self._vlabels[i]+']'   
          # print '---',i,key,self._vlabels,index,'-> label =',label
          self._labels.append(label)

    # Finished:
    self._vv_executed = True                          # avoid duplication
    return self.vvout(self._vv, index)

  #----------------------------------------------------------------

  def vvout (self, vv, index=None):
    """Helper function to return the required list:
    If an index is specified (int or list of ints), return a list with
    the specified element(s) of vv. Otherwise, return the entire list vv.
    """
    # print '\n** vvout(',index,'):'
    if isinstance(index,int):
      return [vv[index]]
    elif isinstance(index,(list,tuple)):
      vvv = [] 
      for i in index:
        vvv.append(vv[i])
        # print '-- index=',index,':',i,vv[i],'->',vvv
      return vvv
    return vv

  #----------------------------------------------------------------

  def VV(self, index=None):
    """Return a list of VV (straight) values."""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._VV, index)


  def vcx(self, index=None):
    """Return a list of vcx (complex) values."""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._vcx, index)


  def dvv(self, index=None):
    """Return a list of dvv (stddev) values."""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._dvv, index)


  def labels(self, index=None):
    """Return a list of labels"""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._labels, index)


  def xx(self, index=None):
    """Return a list of x-coordinates"""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._xx, index)


  def dxx(self, index=None):
    """Return a list of error-bars for x-coordinates"""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._dxx, index)


  def yy(self, index=None):
    """Return a list of x-coordinates"""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._yy, index)


  def dyy(self, index=None):
    """Return a list of error-bars for x-coordinates"""
    if not self._vv_executed: self.vv()       
    return self.vvout(self._dyy, index)






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

  def sigmabar (self):
    """Return the length of the one_sigma-bar (stddev) around the mean.
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
    # print '\n** cells =',cells
    domain = cells['domain']
    # print '- domain =',domain
    if domain.has_key('axis_map'):
      axes = list(cells['domain']['axis_map'])
    else:
      axes = ['time','freq']
    # print '- axes =',axes

    cs = cells['cell_size']
    self._axes = []
    for i,axis in enumerate(axes):
      axis = str(axis).lower()
      if cs.has_key(axis):
        self._axes.append(axis)

    # Make the correct shape (list):
    self._shape = []
    for key in self._axes:
      if isinstance(cs[key],(list,tuple)):
        self._shape.append(len(cs[key]))
      else:
        self._shape.append(1)

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
    ss = '** <Cells>:'
    ss += ' '+str(self.len())
    ss += ' '+str(self.shape())
    ss += ' '+str(self._axes)
    return ss
                              
  def show (self):
    show_value(self._cells)
    return True







#=====================================================================================
# Make a pyNode with one child to be unpacked:
#=====================================================================================


class OneChildPyNode (pynode.PyNode):
  """Make a test pyNode that uses the Result class"""

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


class MultiChildPyNode (pynode.PyNode):
  """Make a test pyNode that uses the ResultVector class"""

  def __init__ (self, *args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution');
                              
  def get_result (self, request, *children):
    rv = ResultVector(children, offset=0.0)
    rv = ResultVector(children, xindex=1, yindex=2,
                      vlabels=['P','Q'],
                      labels=['a','b','c','d'])
    rv.display(full=True)
    return children[0]




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

    if False:
      cc = []
      cc.append(ns['XX'] << 1+1j)
      cc.append(ns['XY'] << -1+1j)
      cc.append(ns['YX'] << -1-1j)
      cc.append(ns['YY'] << 1-1j)
      c = ns['child'] << Meq.Composer(*cc)

    elif True:
      cc = []
      cc.append(ns['123'] << Meq.Composer(1,2,3))
      cc.append(ns['456'] << Meq.Composer(4,5,6))
      cc.append(ns['789'] << Meq.Composer(7,8,9))
      c = ns['child'] << Meq.Composer(*cc)

    if False:
      classname = "OneChildPyNode"
      ns.pynode << Meq.PyNode(c, class_name=classname, module_name=__file__)
    else:
      classname = "MultiChildPyNode"
      ns.pynode << Meq.PyNode(children=cc, class_name=classname, module_name=__file__)
                
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
