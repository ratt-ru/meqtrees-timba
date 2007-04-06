# file ../Meow/Position.py

from Timba.TDL import *
from Timba.Meq import meq
from Parameterization import *


class Position (Parameterization):
  """A Position represents a location in 1,2,3,4 diminsional space.
  Its dimensionality depends on the coordinates (x,y,z,t) that are
  specified at creation. These may be numbers or nodes.
  """;
  def __init__(self, ns, name,
               x=None, y=None, z=None, t=None,
               quals=[],kwquals={}):
    Parameterization.__init__(self,ns,name,
                              quals=quals,kwquals=kwquals)
    self.dims = [0,0,0,0]       # i.e. [x,y,z,t]
    if not y==None:
      self.dims[0] = 1
      self._add_parm('xpos', x, tags=['position','xpos'])
    if not y==None:
      self.dims[1] = 1
      self._add_parm('ypos', y, tags=['position','ypos'])
    if not z==None:
      self.dims[2] = 1
      self._add_parm('zpos', z, tags=['position','zpos'])
    if not t==None:
      self.dims[3] = 1
      self._add_parm('tpos', t, tags=['position','tpos'])


  def xyz (self):
    """Returns the xyt 3-vector node for this position."""
    if self.dims[0]*self.dims[1]*self.dims[2]==0:
      raise ValueError,'Position does not have enough dimensions' 
    xyz = self.ns.xyz
    if not xyz.initialized():
      x = self._parm('xpos')
      y = self._parm('ypos')
      z = self._parm('zpos')
      # print str(x),str(y),str(z)
      xyz << Meq.Composer(x,y,z)
    return xyz


#================================================================
    
if __name__ == '__main__':
    ns = NodeScope()
    p1 = Position(ns,'p1', x=1, y=2, z=(ns << Meq.Parm(6.5)))
    xyz = p1.xyz()
    print str(xyz)
