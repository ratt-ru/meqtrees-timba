# file ../JEN/Vector/Vector.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import display
from numarray import *

Settings.forest_state.cache_policy = 100


#================================================================

class Vector (Meow.Parameterization):
  """Represents a N-dimensional vector """
  
  def __init__(self, ns, name, elem=[], axes=['x','y','z','t'], 
               unit=None, quals=[], kwquals={}, tags=[], solvable=True,
               test=False):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)
    self._unit = unit
    self._axes = []
    for k,item in enumerate(elem):
      axis = axes[k]
      self._axes.append(axis)
      if is_node(item):
        test = False
        self._add_parm(axis, (self.ns[axis] << Meq.Identity(item)),
                       tags=tags, solvable=solvable)
      elif isinstance(item, Meow.Parm):
        test = False
        self._add_parm(axis, item, tags=tags, solvable=solvable)
      else:
        self._add_parm(axis, item, tags=tags, solvable=solvable)
  
    # The following is only for testing: It is assumed that the items
    # are numeric, so we can turn them into a numarray.array:
    self._test = test
    self._test_value = []
    if self._test:
      for k,item in enumerate(elem):
        self._test_value.append(item)
      self._test_value = array(self._test_value)

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
    axis = self.axis(key)
    return self._parm(axis)

  def list (self):
    """Returns the list of elements (nodes) of this Vector."""
    cc = []
    for axis in self._axes:
      cc.append(self._parm(axis))
    return cc

  def commensurate(self, other):
    """Return True if commensurate with the given (other) Vector"""
    s = None
    if not isinstance(other, Vector):
      s = 'other is not a Vector, but: '+str(type(other))
    elif not self.len()==other.len():  
      s = 'Vector length mismatch: '+str(other.len())+' != '+str(self.len())
    if s: raise ValueError,s
    return True                    

  #-------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    ss += ' '+str(self.name)+': '+str(self._axes)
    if self._test:
      ss += '='+str(self._test_value)
    if self._unit:
      ss += ' (unit='+str(self._unit)+')'
    return ss

  #---------------------------------------------------------------------

  def _show_test_result(self, node, other=None, show=True):
    """Helper function to print the test_result. for comparison with
    the result of the named node in the meqbrowser."""
    if show: display.subtree(node, node.name)
    ss = '** test: the result of node:  '+node.name
    ss += '  should be:  '+str(self._test_result)
    print '\n',ss,'\n'
    return ss


  #---------------------------------------------------------------------
  # Methods that produce a node:
  #---------------------------------------------------------------------

  def node (self, show=False):
    """Returns the n-element 'tensor' node for this Vector."""
    node = self.ns['Vector']
    if not node.initialized():
      node << Meq.Composer(*self.list())
    if self._test:
      self._test_result = self._test_value
      self._show_test_result(node, show=False)
    if show:
      display.subtree(node, node.name)
    return node

  #---------------------------------------------------------------------

  def magnitude (self, show=False):
    """Returns the magnitude (node) for this Vector."""
    node = self.ns['magnitude']
    if not node.initialized():
      cc = self.list()
      for k,c in enumerate(cc):
        cc[k] = node('Sqr')(k) << Meq.Sqr(c)
      ssq = node('SumSqr') << Meq.Add(*cc)
      node << Meq.Sqrt(ssq)
    if self._test:
      self._test_result = sqrt(sum(self._test_value*self._test_value))
      self._show_test_result(node, show=show)
    return node


  #---------------------------------------------------------------------
  # Binary vector operations (require another vector):
  #---------------------------------------------------------------------

  def dot_product (self, other, show=False):
    """Returns the dot-product (node) bewteen itself and another Vector"""
    self.commensurate(other)
    node = self.ns['dot_product'].qadd(other.ns)
    if not node.initialized():
      cc1 = self.list()
      cc2 = other.list()
      for k,c in enumerate(cc1):
        cc1[k] = node('Multiply')(k) << Meq.Multiply(cc1[k],cc2[k])
      node << Meq.Add(*cc1)
    if self._test:
      self._test_result = sum(self._test_value*other._test_value)
      self._show_test_result(node, other, show=show)
    return node

  #---------------------------------------------------------------------

  def enclosed_angle (self, other, show=False):
    """Returns the enclosed angle (node, rad) between itself and another Vector"""
    self.commensurate(other)
    node = self.ns['enclosed_angle'].qadd(other.ns)
    if not node.initialized():
      dp = self.dot_product(other)
      m1 = self.magnitude()
      m2 = other.magnitude()
      node << Meq.Divide(dp,(m1*m2))
    if self._test:
      dp = sum(self._test_value*other._test_value)
      m1 = sqrt(sum(self._test_value*self._test_value))
      m2 = sqrt(sum(other._test_value*other._test_value))
      self._test_result = dp/(m1*m2)
      self._show_test_result(node, other, show=show)
    return node

  #---------------------------------------------------------------------
  # Methods that produce another Vector object:
  #---------------------------------------------------------------------

  def binop (self, other):
    """Add the elements"""
    return False








  #---------------------------------------------------------------------

  def zenith_angle(self):
    """Return the zenith angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course.
    Clumsy, but tested. Works fine."""
    zang = self.ns.zenith_angle
    if not zang.initialized():
      xyz1 = self._satellite.xyz()
      xyz2 = self._station.xyz()
      dxyz = zang('dxyz') << Meq.Subtract(xyz1,xyz2)
      prod11 = zang('prod11') << Meq.Sqr(xyz2)
      prod22 = zang('prod22') << Meq.Sqr(dxyz)
      prod12 = zang('prod12') << Meq.Multiply(xyz2,dxyz)
      cc11 = []
      cc22 = []
      cc12 = []
      for index in [0,1,2]:
        cc11.append(zang('cc11')(index) << Meq.Selector(prod11, index=index))
        cc22.append(zang('cc22')(index) << Meq.Selector(prod22, index=index))
        cc12.append(zang('cc12')(index) << Meq.Selector(prod12, index=index))
      sum12 = zang('sum12') << Meq.Add(*cc12)
      ssq12 = zang('ssq12') << Meq.Multiply((zang('ssq1') << Meq.Add(*cc11)),
                                            (zang('ssq2') << Meq.Add(*cc22)))
      norm = zang('norm') << Meq.Sqrt(ssq12)
      cosz = zang('cos') << Meq.Divide(sum12, norm)
      zang << Meq.Acos(cosz)
    return zang


#===============================================================

class Vector2D (Vector):
  """Represents a 2-dimensional Vector, i.e. a Vector with some extra methods"""
  
  def __init__(self, ns, name, elem=[], axes=['x','y'], 
               unit=None, quals=[], kwquals={},
               tags=[], solvable=True,
               test=False):

    if not len(elem)==2:
      s = 'Vector2D should have 2 elements, not:'+str(len(elem))
      raise ValueError,s

    Vector.__init__(self, ns, name=name, elem=elem, axes=axes, 
                    unit=unit, quals=quals, kwquals=kwquals,
                    tags=tags, solvable=solvable,
                    test=test)
    return None

  #---------------------------------------------------------------------

  def rotate (self, angle=0.0, show=False):
    """Returns a Composer (node) for this Vector rotated by the given angle.
    The latter may be a number or a node."""
    node = self.ns['rotated'](str(angle)+'rad')
    if not node.initialized():
      a = node('rotation_angle') << angle
      cosa = node('cos') << Meq.Cos(a)
      sina = node('sin') << Meq.Sin(a)
      nsin = node('nsin') << Meq.Negate(sina)
      cc = self.list()
      node << Meq.Composer(cosa*cc[0] + sina*cc[1],
                           nsin*cc[1] + cosa*cc[0])
    return node



#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    v1 = Vector(ns, 'v1', [1,2,12], test=True, unit='m')
    print v1.oneliner()

    cc.append(v1.node(show=True))
    cc.append(v1.magnitude(show=True))

    v2 = Vector(ns, 'v2', [1,2,-3], test=True, unit='m')
    print v2.oneliner()

    cc.append(v1.dot_product(v2, show=True))
    cc.append(v1.enclosed_angle(v2, show=True))

    ns.result << Meq.Composer(children=cc)
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

    v1 = Vector(ns, 'v1', [1,2,12], test=True, unit='m')
    print v1.oneliner()
    v2 = Vector(ns, 'v2', [1,2,3], test=True, unit='m')
    print v2.oneliner()

    if 0:
      node = v1.enclosed_angle(v2, show=True)

    if 0:
      node = v1.dot_product(v2, show=True)

    if 0:
      node = v1.magnitude(show=True)

    if 0:
      node = v1.node(show=True)

    #---------------------------------------------------

    if 0:
      v3 = Vector(ns, 'v3', v1.list())
      print v3.oneliner()
      for key in range(v3.len()):
        node = v3.element(key)
        print '- element(',key,'): ',str(node)
      node = v3.node(show=True)

    if 0:
      for key in range(v1.len()):
        node = v1.element(key)
        print '- element(',key,'): ',str(node)
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

    #-----------------------------------------------------------

    if 1:
      t1 = Vector2D(ns, 't1', [1,2], test=True, unit='m')
      print t1.oneliner()
    
      if 1:
        node = t1.rotate(angle=1.0, show=True)
        display.subtree(node, node.name)
