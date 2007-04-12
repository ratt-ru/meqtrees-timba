# file ../JEN/Vector/Vector.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import display
from numarray import *

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
    self._typename = str(typename)        # used in .node() below

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
        node = self.ns[axis]
        if not node.initialized():
          node << Meq.Selector(self._tensor_node, index=index)
        return node
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
        pass                                         # OK
      elif isinstance(other,(int,float,complex)):
        pass                                         # OK
      else:
        s = 'other type not recognized: '+str(type(other))
    elif not self.len()==other.len():  
      s = 'Vector length mismatch: '+str(other.len())+' != '+str(self.len())
    if s: raise ValueError,s
    return True                    

  #-------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    if not self._typename=='Vector':
      ss += ' ('+str(self._typename)+')'
    ss += '  '+str(self.name)+'  '+str(self._axes)
    if self._test:
      ss += '='+str(floor(self._test['elem']))
    if self._unit:
      ss += '  (unit='+str(self._unit)+')'
    return ss

  #---------------------------------------------------------------------

  def _show_subtree(self, node, show=False, recurse=5):
    """Helper function to show the subtree under the given node"""
    if show:
      self.test_result(show=show)
      print '\** Subtree result from:',self.oneliner()
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

  def node (self, name=None, show=False):
    """Returns the n-element 'tensor' node for this Vector."""
    if not isinstance(name,str):
      name = self._typename                   # default: 'Vector'
    node = self.ns[name]
    if not node.initialized():
      if self._tensor_node:
        node << Meq.Identity(self._tensor_node)
      else:
        node << Meq.Composer(*self.list())
    self._show_subtree(node, show=show)
    return node

  #---------------------------------------------------------------------

  def magnitude (self, show=False):
    """Returns the magnitude (node) for this Vector."""
    name = 'magnitude'
    node = self.ns[name]
    if not node.initialized():
      cc = self.list()
      for k,c in enumerate(cc):
        cc[k] = node('Sqr')(k) << Meq.Sqr(c)
      ssq = node('SumSqr') << Meq.Add(*cc)
      if self._test:
        self._test[name] = sqrt(sum(self._test['elem']*self._test['elem']))
        node << Meq.Sqrt(ssq, testval=self._test[name])
      else:
        node << Meq.Sqrt(ssq)
    self._show_subtree(node, show=show)
    return node


  #---------------------------------------------------------------------
  # Binary vector operations (require another vector):
  #---------------------------------------------------------------------

  def dot_product (self, other, show=False):
    """Returns the dot-product (node) bewteen itself and another Vector"""
    self.commensurate(other)
    name = 'dot_product'
    node = self.ns[name].qadd(other.ns)
    if not node.initialized():
      cc1 = self.list()
      cc2 = other.list()
      for k,c in enumerate(cc1):
        cc1[k] = node('Multiply')(k) << Meq.Multiply(cc1[k],cc2[k])
      if self._test and other._test:
        self._test['other'] = other.oneliner()
        self._test[name] = sum(self._test['elem']*other._test['elem'])
        node << Meq.Add(children=cc1, testval=self._test[name])
      else:
        node << Meq.Add(*cc1)
    self._show_subtree(node, show=show)
    return node

  #---------------------------------------------------------------------

  def enclosed_angle (self, other, show=False):
    """Returns the enclosed angle (node, rad) between itself and another Vector"""
    self.commensurate(other)
    name = 'enclosed_angle'
    node = self.ns[name].qadd(other.ns)
    if not node.initialized():
      dp = self.dot_product(other)
      m1 = self.magnitude()
      m2 = other.magnitude()
      cosa = node('cos') << Meq.Divide(dp,(m1*m2))
      if self._test and other._test:
        self._test['other'] = other.oneliner()
        dp = sum(self._test['elem']*other._test['elem'])
        m1 = sqrt(sum(self._test['elem']*self._test['elem']))
        m2 = sqrt(sum(other._test['elem']*other._test['elem']))
        self._test[name] = arccos(dp/(m1*m2))
        node << Meq.Acos(cosa, testval=self._test[name])
      else:
        node << Meq.Acos(cosa)
    self._show_subtree(node, show=show)
    return node

  #---------------------------------------------------------------------
  # Methods that produce another Vector object:
  #---------------------------------------------------------------------

  def binop (self, binop, other, name=None, quals=[], show=False):
    """Returns another Vector object which is the result of the specified
    binary operation (e.g. binop='Subtract') between itself and another Vector"""
    self.commensurate(other, severe=False)

    if isinstance(other, Vector):
      node = self.ns[binop].qadd(other.ns)
      if not node.initialized():
        node << getattr(Meq,binop)(self.node(),other.node())
    elif is_node(other):
      node = self.ns[binop].qadd(other)
      if not node.initialized():
        node << getattr(Meq,binop)(self.node(),other)
    else:
      # Assume numeric value: 
      node = self.ns[binop](str(other))
      if not node.initialized():
        node << getattr(Meq,binop)(self.node(),other)

    self._show_subtree(node, show=show)
      
    # Make a new Vector object:
    if isinstance(name, str):
      # Name is specified: make a new start (ns0, quals):
      vout = Vector(self.ns0, name, node, nelem=self.len(), quals=quals)
    elif isinstance(other, Vector):
      vout = Vector(self.ns, binop, node, nelem=self.len(), quals=other.ns.quals)
    elif is_node(other):
      vout = Vector(self.ns, binop, node, nelem=self.len(), quals=other.quals)
    else:
      vout = Vector(self.ns, binop, node, nelem=self.len(), quals=str(other))

    if show:
      vout.list(show=True)
      self._show_subtree(vout.node(), show=show)
    return vout









#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    v1 = Vector(ns, 'v1', [1,2,12], unit='m')
    print v1.oneliner()

    cc.append(v1.node(show=True))
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

    if 0:
      other = v2
      other = ns['other']('qual') << Meq.Constant(56)
      other = 78
      v4 = v1.binop('Add', other, name='xxx', show=True)
      
    if 1:
      node = v1.enclosed_angle(v2, show=True)

    if 0:
      node = v1.dot_product(v2, show=True)

    if 0:
      node = v1.magnitude(show=True)

    if 0:
      node = v1.node(show=True)

    if 0:
      v1.test_result(show=True)

    #---------------------------------------------------

    if 0:
      node = ns['tensor'] << Meq.Composer(1,2,3)
      v3 = Vector(ns, 'v3', node, nelem=3)
      print v3.oneliner()
      v3.node(show=True)
      v3.list(show=True)
      v3.magnitude(show=True)


    if 0:
      v3 = Vector(ns, 'v3', v1.list())
      print v3.oneliner()
      for key in range(v3.len()):
        node = v3.element(key)
        print '- element(',key,'): ',str(node)
      cc = v3.list(show=True)
      node = v3.node(show=True)

    if 0:
      for key in range(v1.len()):
        node = v1.element(key)
        print '- element(',key,'): ',str(node)
      cc = v1.list(show=True)
      node = v1.node(show=True)

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


