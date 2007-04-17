# file ../JEN/Vector/GeoLocation.py

from Timba.TDL import *
from Timba.Meq import meq

# from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Vector import Vector
from numarray import *
from copy import deepcopy

Settings.forest_state.cache_policy = 100

#================================================================

class GeoLocation (Vector.Vector):
  """Represents a location Vector (X,Y,Z) w.r.t. the Earth centre,
  which may or may not lie on the Earth surface. Unit in km.
  The Earth axis is the Z-axis, with North positive.
  The positive Y-axis intersects the Greenwich meridian.
  For a vector magnitude R, we have the following definitions:
  X ~ R.cos(latitude).sin(longitude)
  Y ~ R.cos(latitude).cos(longitude)
  Z ~ R.sin(latitude)
  """

  def __init__(self, ns, name,
               longlat=None, radius=None,
               xyz=[], nelem=3,
               quals=[],kwquals={},
               tags=[], solvable=False):

    self._Earth = dict(radius=6378, flattening=3.36e-6)

    if longlat:                              # [long,lat] specified
      if radius==None:
        radius = self._Earth['radius']       # assume Earth surface point

      node = ns['xyz']('longlat')(name)(*quals)(**kwquals)
      lat = None
      if is_node(longlat):                   # assume [long,lat] composer
        lon = node('longitude') << Meq.Selector(longlat, index=0)
        lat = node('latitude') << Meq.Selector(longlat, index=1)

      if isinstance(longlat,(list,tuple)):
        if is_node(longlat[0]):              # assume [long,lat] nodes
          lon = longlat[0]
          lat = longlat[1]
        else:                                # assume [long,lat] numeric
          # Make numeric [x,y,z]:
          xyz = [radius*cos(longlat[1])*sin(longlat[0]),
                 radius*cos(longlat[1])*cos(longlat[0]),
                 radius*sin(longlat[1])]
      if lat:
        # Make [x,y,z] nodes:
        clong = node('coslong') << Meq.Cos(lon)
        slong = node('sinlong') << Meq.Sin(lon)
        clat = node('coslat') << Meq.Cos(lat)
        slat = node('sinlat') << Meq.Sin(lat)
        X = node('X') << Meq.Multiply(radius,clat,slong)
        Y = node('Y') << Meq.Multiply(radius,clat,clong)
        Z = node('Z') << Meq.Multiply(radius,slat)
        xyz = [X,Y,Z]


    Vector.Vector.__init__(self, ns=ns, name=name,
                           elem=xyz, nelem=3,
                           quals=quals, kwquals=kwquals,
                           tags=tags, solvable=solvable,
                           typename='GeoLocation',
                           axes=['X','Y','Z'], unit='km')


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
        


  #=====================================================================
  # Functions that require another GeoLocation object:
  #=====================================================================

  def longlat_diff(self, other, quals=[], show=False):
    """Return the [longtitude,latitude] difference between
    another GeoLocation node and itself."""
    name = 'longlat_diff'
    if not isinstance(quals,(list,tuple)): quals = [quals]
    qnode = self.ns[name].qmerge(other.ns['GeoLocation_dummy_qnode'])(*quals) 
    if not qnode.initialized():
      qnode << Meq.Subtract(other.longlat(), self.longlat())
    self._show_subtree(qnode, show=show, recurse=4)
    return qnode

  #-------------------------------------------------------

  def zenith_angle(self, other, quals=[], show=False):
    """Return the zenith angle (node) of another GeoLocation,
    as seen from itself."""
    name = 'zenith_angle'
    if not isinstance(quals,(list,tuple)): quals = [quals]
    qnode = self.ns[name].qmerge(other.ns['GeoLocation_dummy_qnode'])(*quals) 
    if not qnode.initialized():
      dxyz = other.binop('Subtract', self) 
      encl = self.enclosed_angle(dxyz)
      qnode << Meq.Identity(encl)
    self._show_subtree(qnode, show=show, recurse=4)
    return qnode

  #-------------------------------------------------------

  def elevation(self, other, quals=[], show=False):
    """Return the elevation angle (node) of another GeoLocation,
    as seen from itself."""
    name = 'elevation'
    if not isinstance(quals,(list,tuple)): quals = [quals]
    qnode = self.ns[name].qmerge(other.ns['GeoLocation_dummy_qnode'])(*quals) 
    if not qnode.initialized():
      zang = self.zenith_angle(other, quals=quals)
      qnode << Meq.Subtract(pi/2.0, zang)
    self._show_subtree(qnode, show=show, recurse=4)
    return qnode

  #-------------------------------------------------------

  def azimuth(self, other, quals=[], show=False):
    """Return the azimuth angle (node) of another GeoLocation
    as seen from itself."""
    name = 'azimuth'
    if not isinstance(quals,(list,tuple)): quals = [quals]
    qnode = self.ns[name].qmerge(other.ns['GeoLocation_dummy_qnode'])(*quals) 
    if not qnode.initialized():
      dll = self.longlat_diff(other, quals=quals)
      dlong = qnode('dlong') << Meq.Selector(dll, index=0)
      dlat = qnode('dlat') << Meq.Selector(dll, index=1)
      tanaz = qnode('tanaz') << Meq.Divide(dlong, dlat)
      qnode << Meq.Atan(tanaz)
    self._show_subtree(qnode, show=show, recurse=4)
    return qnode


  #=============================================================================

  def newObject (self, xyz, name=None, localname='local',
                 quals=[], other=None, show=False):
    """Makes another GeoLocation object from itself, but using the given
    tensor node (xyz) as input. This function is a reimplementation of the
    one in the Vector class, from which GeoLocation is derived."""

    if not isinstance(quals,(list,tuple)): quals = [quals]

    if isinstance(name, str):
      # Name is specified: make a new start (ns0, quals):
      obj = GeoLocation(self.ns0, name, xyz=xyz, quals=quals)
      
    elif isinstance(other, Vector.Vector):
      qq = deepcopy(list(other.ns['GeoLocation_dummy_qnode'].quals))
      qq.extend(quals)
      obj = GeoLocation(self.ns, localname, xyz=xyz, quals=qq)

    elif is_node(other):
      qq = deepcopy(list(other.quals))
      qq.extend(quals)
      obj = GeoLocation(self.ns, localname, xyz=xyz, quals=qq)

    else:
      qq = [str(other)]
      qq.extend(quals)
      obj = GeoLocation(self.ns, localname, xyz=xyz, quals=qq)

    if show:
      obj.list(show=True)
      obj._show_subtree(obj.node(), show=show)
    return obj





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
        if isinstance(g1, GeoLocation):
          print 'g1 is a GeoLocation object'
        if isinstance(g1, Vector.Vector):
          print 'g1 is a Vector object'

      if 1:
        # other = v2
        other = ns['other']('qual') << Meq.Constant(56)
        other = 78
        g4 = g1.binop('Add', other, name='xxx', show=True)
        print g4.oneliner()

      if 0:
        xyz = g1.node(show=True)

      if 0:
        g1.longlat(show=True)

      if 0:
        g1.longlat_complex(show=True)

      if 0:
        g1.altitude(show=True)

      if 0:
        g1.test_result()


    
