# file ../Meow/Position.py

from Timba.TDL import *
from Timba.Meq import meq
from Parameterization import *


class Position (Vector):
  """A Position represents a location in 1,2,3,4 diminsional space.
  Its dimensionality depends on the coordinates (x,y,z,t) that are
  specified at creation. These may be numbers or nodes.
  """;
  def __init__(self, ns, name, elem=[], axes=['x','y','z','t'], 
               unit=None, quals=[], kwquals={}, tags=[], solvable=True,
               test=False):
    
    Vector__init__(self, ns, name, elem=[], axes=['x','y','z','t'], 
                   unit=None, quals=[], kwquals={}, tags=[], solvable=True,
                   test=False):

#================================================================
    
if __name__ == '__main__':
    ns = NodeScope()
    p1 = Position(ns,'p1', x=1, y=2, z=(ns << Meq.Parm(6.5)))
    xyz = p1.xyz()
    print str(xyz)
