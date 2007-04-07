# file ../JEN/projects/MIM/GPS/MIM.py

from Timba.TDL import *
from Timba.Meq import meq
# from Parameterization import *

import Meow

from Timba.Contrib.JEN.Grunt import display
from numarray import *

Settings.forest_state.cache_policy = 100



#================================================================

class MIM (object):
  """Represents a Minimum Ionospheric Model (MIM)"""
  
  def __init__(self, ns, 
               name='MIM', quals=[],kwquals={}):

    self._name = name
    self.ns = Meow.QualScope(ns, quals=quals, kwquals=kwquals)
    return None


  def name (self):
    """Return the object name"""
    return self._name

  def oneliner (self):
    ss = 'MIM: '+str(self.name())
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print
    return True

  #-------------------------------------------------------

  def TEC(self, station, dir0):
    """Return a node/subtree that produces a predicted TEC value for
    a specified station (position) and look direction"""
    node = None
    return node




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    st1 = GPSStation(ns,'st1', pos1)
    sat1 = GPSSatellite(ns,'sat1', x=pos2[0], y=pos2[1], z=pos2[2])
    pair = GPSPair (ns, station=st1, satellite=sat1)
    pair.display(full=True)
    
    cc.append(zang)

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       

#================================================================
# Test program
#================================================================
    
if __name__ == '__main__':
    """Test program"""
    ns = NodeScope()

    st1 = GPSStation(ns, 'st1', [1,2,12])

    sat1 = GPSSatellite(ns, 'sat1', x=4, y=7, z=8)

    pair = GPSPair (ns, station=st1, satellite=sat1)
    pair.display(full=True)

#===============================================================

