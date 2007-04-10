# file ../JEN/Vector/Vector2D.py

from Timba.TDL import *
from Timba.Meq import meq

import Vector

from numarray import *

Settings.forest_state.cache_policy = 100


#================================================================================

class Vector2D (Vector.Vector):
  """Represents a 2-dimensional Vector, i.e. a Vector with some extra methods"""
  
  def __init__(self, ns, name, elem=[], axes=['x','y'], 
               unit=None, quals=[], kwquals={},
               tags=[], solvable=True):

    if not len(elem)==2:
      s = 'Vector2D should have 2 elements, not:'+str(len(elem))
      raise ValueError,s

    Vector.Vector.__init__(self, ns, name=name, elem=elem, axes=axes, 
                           unit=unit, quals=quals, kwquals=kwquals,
                           tags=tags, solvable=solvable)
    return None

  #---------------------------------------------------------------------

  def rotate (self, angle=0.0, show=False):
    """Returns a Composer (node) for this Vector rotated by the given angle.
    The latter may be a number or a node."""
    if is_node(angle):
      node = self.ns['rotated'].qadd(angle)
      a = angle
    else:
      node = self.ns['rotated'](str(angle)+'rad')
      a = node('rotation_angle') << angle
    if not node.initialized():
      cosa = node('cos') << Meq.Cos(a)
      sina = node('sin') << Meq.Sin(a)
      nsin = node('nsin') << Meq.Negate(sina)
      cc = self.list()
      node << Meq.Composer(cosa*cc[0] + sina*cc[1],
                           nsin*cc[1] + cosa*cc[0])
    self._show_subtree(node, show=show)
    return node



#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []


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
    print
    ns = NodeScope()

    if 1:
      t1 = Vector2D(ns, 't1', [1,2], unit='m')
      print t1.oneliner()
    
      if 1:
        angle = 0.8
        angle = ns.angle << 0.9
        node = t1.rotate(angle=angle, show=True)

      if 1:
        t1.test_result()
