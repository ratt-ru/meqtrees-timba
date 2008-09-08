# file ../JEN/Vector/Vector.py

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

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import display
# from num array import *   replaced with numpy
from numpy import *
from copy import deepcopy

Settings.forest_state.cache_policy = 100


#================================================================

class Vector (Meow.Parameterization):
  """Represents a N-dimensional vector. The input can be either a list
  of numeric constants, nodes, or Meow.Parm objects, or a tensor node.
  The elements are labelled according to the axes argument, which has
  default ['x','y','z','y'], but may be user-defined. The Vector class
  inherits from Meow.Parameterization."""
  
  def __init__(self, ns, name, elem=[], nelem=None,
               quals=[], kwquals={},
               tags=[], solvable=True,
               axes=['x','y','z','t'],
               typename='Vector',
               unit=None):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)
    self._unit = unit
    self._typename = str(typename)        # used in .tensornode() below

    self._axes = []
    self._tensor_node = None
    
    test = True
    if is_node(elem):                     # Assume a tensor node
      self._tensor_node = elem
      test = False
      for index in range(nelem):          # NB: nelem must be specified!
        axis = axes[index]
        self._axes.append(axis)
        # self._add_parm(axis, (self.ns[axis] << Meq.Selector(elem, index=index)))

    elif not isinstance(elem,(list,tuple)):
      s = 'elem is not a list, but: '+str(type(elem))
      raise ValueError,s

    else:
      for k,item in enumerate(elem):
        axis = axes[k]
        self._axes.append(axis)
        if is_node(item):                   # item is a node 
          test = False
          self._add_parm(axis, (self.ns[axis] << Meq.Identity(item)),
                         tags=tags, solvable=solvable)
        elif isinstance(item, Meow.Parm):   # item is a Meow.Parm object
          test = False
          self._add_parm(axis, item, tags=tags, solvable=solvable)
        else:                               # assume numeric
          self._add_parm(axis, item, tags=tags, solvable=solvable)

  
    # The following is only for testing: It is assumed that the items
    # in elem are numeric, so we can turn them into a numarray.array:
    self._test = None
    if test:
      self._test = dict(test=test, elem=[]) 
      for k,item in enumerate(elem):
        self._test['elem'].append(item)
      self._test['elem'] = array(self._test['elem'])

    return None

  #---------------------------------------------------------------------

  def len (self):
    """Return the Vector length/dimensionality"""
    return len(self._axes)

  def unit (self):
    """Return the measurement unit (e.g. m or km)"""
    return self._unit

  def axes (self):
    """Return the (list of) Vector axes (name)"""
    return self._axes

  def index (self, key=None):
    """Return the index of the specified (key) Vector axis (str/int)"""
    if isinstance(key, str):
      if key in self._axes: return self._axes.index(key)               # OK
      s = 'Vector axis not recognised: '+str(key)+' '+str(self._axes)
    elif isinstance(key, int):
      if key>=0 and key<len(self._axes): return key                    # OK
      s = 'Vector axis out of range: '+str(key)+' '+str(self._axes)
    else:
      s = 'Illegal Vector axis: '+str(key)+' '+str(type(key))
    raise ValueError,s                                                 # not OK

  def axis(self, key=None):
    """Return the specified (key) Vector axis (name)"""
    return self._axes[self.index(key)]

  def element(self, key=None):
    """Return the specified (key) element (node) of this Vector."""
    index = self.index(key)
    axis = self._axes[index]
    if self._tensor_node:
        qnode = self.ns[axis]
        if not qnode.initialized():
          qnode << Meq.Selector(self._tensor_node, index=index)
        return qnode
    else:
      return self._parm(axis)

  def list (self, show=False):
    """Returns the list of elements (nodes) of this Vector."""
    cc = []
    for axis in self._axes:
      cc.append(self.element(axis))
    if show:
      print '\n** Elements of:',self.oneliner()
      for c in cc: print '   -',str(c)
      print
    return cc


  def commensurate(self, other, severe=True):
    """Return True if commensurate with the given (other) Vector"""
    s = None
    if not isinstance(other, Vector):
      if severe:
        s = 'other is not a Vector, but: '+str(type(other))
      elif is_node(other):
        pass                                         # OK, commensurate
      elif isinstance(other,(int,float,complex)):
        pass                                         # OK, commensurate
      else:
        s = 'other type not recognized: '+str(type(other))
    elif not self.len()==other.len():                
      s = 'Vector length mismatch: '+str(other.len())+' != '+str(self.len())
    if s: raise ValueError,s
    return True                    

  #-------------------------------------------------------

  def oneliner (self):
    """Return a one-line summary of this object."""
    return self.oneliner_common()

  def oneliner_common (self):
    """Make the common part of the oneliner."""
    ss = str(type(self))
    if not self._typename=='Vector':
      ss += ' ('+str(self._typename)+')'
    ss = '*** '+str(self._typename)+': '                    # better?
    ss += '  '+str(self.name)+'  '+str(self._axes)
    if self._test:
      ss += '='+str(floor(self._test['elem']))
    if self._unit:
      ss += '  (unit='+str(self.unit())+')'
    return ss

  #---------------------------------------------------------------------

  def _show_subtree(self, node, show=False, test=False, recurse=5):
    """Helper function to show the subtree under the given node"""
    if show:
      if test:
        self.test_result(show=show)
      print '\n** Subtree result from:',self.oneliner()
      display.subtree(node, node.name, recurse=recurse)
    return True
    

  #---------------------------------------------------------------------

  def test_result(self, show=True):
    """Helper routine to show the test results"""
    if show and isinstance(self._test,dict):
      print '\n** test-results of:',self.oneliner()
      rr = self._test
      for key in rr.keys():
        print '  -',key,':',rr[key]
      print
    return self._test

  #---------------------------------------------------------------------
  # Methods that produce a node:
  #---------------------------------------------------------------------

  def node_obsolete (self, name=None, show=False):
    """Obslolete function call for self.tensornode()"""
    print '\n** Obsolete call to .node(), use .tensornode() instead....\n'
    return self.tensornode (name=name, show=show)

  def tensornode (self, name=None, show=False):
    """Returns the n-element 'tensor' node for this Vector."""
    if not isinstance(name,str):
      name = self._typename                   # default: 'Vector'
    qnode = self.ns[name]
    if not qnode.initialized():
      if self._tensor_node:
        qnode << Meq.Identity(self._tensor_node)
      else:
        qnode << Meq.Composer(*self.list())
    self._show_subtree(qnode, show=show)
    return qnode

  #---------------------------------------------------------------------

  def magnitude (self, quals=[], show=False):
    """Returns the magnitude (node) for this Vector."""
    name = 'magnitude'
    qnode = self.ns[name](quals)
    if not qnode.initialized():
      cc = self.list()
      for k,c in enumerate(cc):
        cc[k] = qnode('Sqr')(k) << Meq.Sqr(c)
      ssq = qnode('SumSqr') << Meq.Add(*cc)
      if self._test:
        self._test[name] = sqrt(sum(self._test['elem']*self._test['elem']))
        qnode << Meq.Sqrt(ssq, testval=self._test[name])
      else:
        qnode << Meq.Sqrt(ssq)
    self._show_subtree(qnode, show=show)
    return qnode


  #---------------------------------------------------------------------
  # Binary vector operations (require another vector):
  #---------------------------------------------------------------------

  def dot_product (self, other, quals=[], show=False):
    """Returns the dot-product (node) bewteen itself and another Vector"""
    self.commensurate(other)
    name = 'dot_product'
    if not isinstance(quals,(list,tuple)): quals = [quals]
    qnode = self.ns[name].qmerge(other.ns['Vector_dummy_qnode'])(*quals)       # <-----!!
    if not qnode.initialized():
      cc1 = self.list()
      cc2 = other.list()
      for k,c in enumerate(cc1):
        axis = self._axes[k]
        cc1[k] = qnode('Multiply')(axis) << Meq.Multiply(cc1[k],cc2[k])
      if self._test and other._test:
        self._test['other'] = other.oneliner()
        self._test[name] = sum(self._test['elem']*other._test['elem'])
        qnode << Meq.Add(children=cc1, testval=self._test[name])
      else:
        qnode << Meq.Add(*cc1)
    self._show_subtree(qnode, show=show)
    return qnode

  #---------------------------------------------------------------------

  def enclosed_angle (self, other, quals=[], show=False):
    """Returns the enclosed angle (node, rad) between itself and another Vector"""
    self.commensurate(other)
    name = 'enclosed_angle'
    if not isinstance(quals,(list,tuple)): quals = [quals]
    qnode = self.ns[name].qmerge(other.ns['Vector_dummy_qnode'])(*quals)       # <-----!!
    if not qnode.initialized():
      dp = self.dot_product(other, quals=quals)
      m1 = self.magnitude(quals=quals)
      m2 = other.magnitude(quals=quals)
      cosa = qnode('cos') << Meq.Divide(dp,(m1*m2))
      if self._test and other._test:
        self._test['other'] = other.oneliner()
        dp = sum(self._test['elem']*other._test['elem'])
        m1 = sqrt(sum(self._test['elem']*self._test['elem']))
        m2 = sqrt(sum(other._test['elem']*other._test['elem']))
        self._test[name] = arccos(dp/(m1*m2))
        qnode << Meq.Acos(cosa, testval=self._test[name])
      else:
        qnode << Meq.Acos(cosa)
    self._show_subtree(qnode, show=show)
    return qnode

  #---------------------------------------------------------------------
  # Methods that produce another Vector object:
  #---------------------------------------------------------------------

  def binop (self, binop, other, name=None, quals=[], show=False):
    """Returns another object of the same type, which is the result of the specified
    binary operation (e.g. binop='Subtract') between itself and another Vector object.
    """
    
    self.commensurate(other, severe=False)

    if not isinstance(quals,(list,tuple)): quals = [quals]

    if isinstance(other, Vector):
      qnode = self.ns[binop].qmerge(other.ns['Vector_dummy_qnode'])(*quals)  
      if not qnode.initialized():
        qnode << getattr(Meq,binop)(self.tensornode(),other.tensornode())
    elif is_node(other):
      qnode = self.ns[binop].qmerge(other)(*quals)
      if not qnode.initialized():
        qnode << getattr(Meq,binop)(self.tensornode(),other)
    else:
      # Assume numeric value: 
      qnode = self.ns[binop](str(other))(*quals)
      if not qnode.initialized():
        qnode << getattr(Meq,binop)(self.tensornode(),other)

    self._show_subtree(qnode, show=show)
    return self.newObject (qnode, name=name, localname=binop,
                           quals=quals, other=other, show=show)


  #=============================================================================

  def newObject (self, xyz, name=None, localname='local',
                 quals=[], other=None, show=False):
    """Makes another Vector object from itself, but using the given
    tensor node (xyz) as input. This function must be reimplemented
    in classes that are derived from Vector (e.g. GeoLocation)"""

    if not isinstance(quals,(list,tuple)): quals = [quals]

    if isinstance(name, str):
      # Name is specified: make a new start (ns0, quals):
      obj = Vector(self.ns0, name,
                   elem=xyz, nelem=self.len(),
                   quals=quals,
                   axes=self._axes)
      
    elif isinstance(other, Vector):
      qq = deepcopy(list(other.ns['Vector_dummy_qnode'].quals))
      qq.extend(quals)
      obj = Vector(self.ns, localname,
                   elem=xyz, nelem=self.len(),
                   quals=qq,
                   axes=self._axes)

    elif is_node(other):
      qq = deepcopy(list(other.quals))
      qq.extend(quals)
      obj = Vector(self.ns, localname,
                   elem=xyz, nelem=self.len(),
                   quals=qq,
                   axes=self._axes)
    else:
      qq = [str(other)]
      qq.extend(quals)
      obj = Vector(self.ns, localname,
                   elem=xyz, nelem=self.len(),
                   quals=qq,
                   axes=self._axes)

    if show:
      obj.list(show=True)
      self._show_subtree(obj.tensornode(), show=show)
    return obj









#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    v1 = Vector(ns, 'v1', [1,2,12], unit='m')
    print v1.oneliner()

    cc.append(v1.tensornode(show=True))
    cc.append(v1.magnitude(show=True))

    v2 = Vector(ns, 'v2', [1,2,-3], unit='m')
    print v2.oneliner()

    cc.append(v1.dot_product(v2, show=True))
    cc.append(v1.enclosed_angle(v2, show=True))

    ns.result << Meq.Composer(children=cc)
    v1.test_result()
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       

#================================================================
# Test program
#================================================================
    
if __name__ == '__main__':
    """Test program"""
    ns = NodeScope()

    v1 = Vector(ns, 'v1', [1,2,12], unit='m')
    print v1.oneliner()
    v2 = Vector(ns, 'v2', [1,2,3], unit='m')
    print v2.oneliner()

    if 1:
      other = v2
      other = ns['other']('qual') << Meq.Constant(56)
      other = 78
      v4 = v1.binop('Add', other, name='xxx', show=True)
      
    if 0:
      node = v1.enclosed_angle(v2, show=True)

    if 0:
      node = v1.dot_product(v2, show=True)

    if 0:
      node = v1.magnitude(show=True)

    if 0:
      node = v1.tensornode(show=True)

    if 0:
      v1.test_result(show=True)

    #---------------------------------------------------

    if 0:
      node = ns['tensor'] << Meq.Composer(1,2,3)
      v3 = Vector(ns, 'v3', node, nelem=3)
      print v3.oneliner()
      v3.tensornode(show=True)
      v3.list(show=True)
      v3.magnitude(show=True)


    if 0:
      v3 = Vector(ns, 'v3', v1.list())
      print v3.oneliner()
      for key in range(v3.len()):
        node = v3.element(key)
        print '- element(',key,'): ',str(node)
      cc = v3.list(show=True)
      node = v3.tensornode(show=True)

    if 0:
      for key in range(v1.len()):
        node = v1.element(key)
        print '- element(',key,'): ',str(node)
      cc = v1.list(show=True)
      node = v1.tensornode(show=True)

    if 0:
      print v1.commensurate(v1)
      # print v1.commensurate([])
      # print v1.commensurate(Vector(ns, 'v2', [1,2]))

    if 0:
      print v1.axes()
      print v1.axis(0)
      print v1.axis('y')
      # print v1.axis(8)
      # print v1.axis('q')
      # print v1.axis()


