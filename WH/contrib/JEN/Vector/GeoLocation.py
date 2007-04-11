# file ../JEN/Vector/GeoLocation.py

from Timba.TDL import *
from Timba.Meq import meq

# from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Vector import Vector
from numarray import *

Settings.forest_state.cache_policy = 100

#================================================================

class GeoLocation (Vector.Vector):
  """Represents a location Vector (X,Y,Z) w.r.t. the Earth centre,
  which may or may not lie on the Earth surface. Unit in meters.
  The Earth axis is the Z-axis, with North positive.
  The positive Y-axis intersects the Greenwich meridian.
  For a vector magnitude R, we have the following definitions:
  X ~ R.cos(latitude).sin(longitude)
  Y ~ R.cos(latitude).cos(longitude)
  Z ~ R.sin(latitude)
  """

  def __init__(self, ns, name, xyz=[],
               longlat=None, radius=None,
               quals=[],kwquals={},
               tags=[], solvable=False):

    self._Earth = dict(radius=6.378e6, flattening=3.36e-6)

    if longlat:                              # [long,lat] specified
      if radius==None:
        radius = self._Earth['radius']       # assume Earth surface point
      xyz = [radius*cos(longlat[1])*sin(longlat[0]),
             radius*cos(longlat[1])*cos(longlat[0]),
             radius*sin(longlat[1])]

    Vector.Vector.__init__(self, ns=ns, name=name, elem=xyz,
                           quals=quals, kwquals=kwquals,
                           tags=tags, solvable=solvable,
                           typename='GeoLocation',
                           axes=['X','Y','Z'], unit='m')


    return None


  #------------------------------------------------------------------

  def latitude (self, show=False):
    """Returns the latitude (rad) = arcsin(Z/R)"""
    self.longlat()
    node = self.ns['latitude']
    self._show_subtree(node, show=show)
    return node
        
  def longitude (self, show=False):
    """Returns the longitude (rad) = arcsin(X/R)"""
    self.longlat()
    node = self.ns['longitude']
    self._show_subtree(node, show=show)
    return node
        
  def longlat_complex (self, show=False):
    """Returns longlat (node) as complex (long+j*lat), for plotting"""
    node = self.ns['longlat_complex']
    if not node.initialized():
      node << Meq.ToComplex(self.longitude(),
                            self.latitude())
    self._show_subtree(node, show=show)
    return node
      
  def longlat (self, show=False):
    """Returns a two-pack with its latitude and longtitude (rad)"""
    node = self.ns['longlat']
    if not node.initialized():
      m = self.magnitude()
      slat = node('slat') << Meq.Divide(self.element('Z'),m)
      latitude = self.ns['latitude'] << Meq.Asin(slat)
      clat = node('clat') << Meq.Cos(latitude)
      slong = node('slong') << Meq.Divide(self.element('X'),(m*clat))
      longitude = self.ns['longitude'] << Meq.Asin(slong)
      if self._test:
        m = self._test['magnitude']
        self._test['latitude'] = arcsin(self._test['elem'][2]/m)
        clat = cos(self._test['latitude'])
        self._test['longitude'] = arcsin(self._test['elem'][0]/(m*clat))
        testval = [self._test['longitude'],self._test['latitude']]
        node << Meq.Composer(longitude,latitude, testval=testval)
      else:
        node << Meq.Composer(longitude, latitude)
      self._show_subtree(node, show=show)
    return node
        

  #------------------------------------------------------------------

  def altitude (self, show=False):
    """Returns the altitude above the Earth surface"""
    name = 'altitude'
    node = self.ns[name]
    if not node.initialized():
      m = self.magnitude()
      R = self._Earth['radius']
      if self._test:
        self._test[name] = self._test['magnitude']-self._Earth['radius']
        node << Meq.Subtract(m, R, testval=self._test[name])
      else:
        node << Meq.Subtract(m, R)
    self._show_subtree(node, show=show)
    return node
        




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    g1 = GeoLocation(ns, 'g1', longlat=[1.1,-0.9])
    print g1.oneliner()

    cc.append(g1.longlat(show=True))
    cc.append(g1.altitude(show=True))

    g1.test_result()
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
    print
    ns = NodeScope()

    if 1:
      # g1 = GeoLocation(ns, 'g1', [1,2,12])
      g1 = GeoLocation(ns, 'g1', longlat=[1.1,-0.9])
      print g1.oneliner()

      if 0:
        xyz = g1.node(show=True)

      if 0:
        g1.longlat(show=True)

      if 1:
        g1.longlat_complex(show=True)

      if 0:
        g1.altitude(show=True)

      if 0:
        g1.test_result()


    
