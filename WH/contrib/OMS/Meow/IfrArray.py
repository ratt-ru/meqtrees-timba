from Timba.TDL import *

class IfrArray (object):
  def __init__(self,ns,station_list,uvw_table=None,mirror_uvw=False):
    self.ns = ns;
    self._stations = station_list;
    self._ifrs = [ (s1,s2) for s1 in station_list for s2 in station_list if s1<s2 ];
    self._uvw_table = uvw_table;
    self._mirror_uvw = mirror_uvw;
    self._jones = [];

  def stations (self):
    return self._stations;
    
  def num_stations (self):
    return len(self._stations);
    
  def ifrs (self):
    return self._ifrs;
    
  def num_ifrs (self):
    return len(self._ifrs);
    
  def xyz0 (self):
    """Returns array reference position node""";
    self.xyz();
    return self.ns.xyz0;
    
  def xyz (self):
    """Returns unqualified station position nodes""";
    xyz0 = self.ns.xyz0;
    if not xyz0.initialized():
      for station in self.stations():
        # create XYZ nodes
        xyz = self.ns.xyz(station) << Meq.Composer(
          self.ns.x(station) << Meq.Constant(0.0),
          self.ns.y(station) << Meq.Constant(0.0),
          self.ns.z(station) << Meq.Constant(0.0)
        );
        if not xyz0.initialized():
          xyz0 << Meq.Selector(xyz); # xyz0 == xyz first station essentially
    return self.ns.xyz;
    
  def uvw (self,radec0,*quals):
    """returns station UVW node(s) for a given phase centre direction.
    If a station is supplied, returns UVW node for that station""";
    uvw = self.ns.uvw.qadd(radec0);
    if not uvw(self.stations()[0]).initialized():
      if not self._uvw_table:
        xyz0 = self.xyz0();
        xyz = self.xyz();
      for station in self.stations():
        # create UVW nodess
        # if a table is specified, UVW will be read in directly
        if self._uvw_table:
          uvw_def = Meq.Composer(
            self.ns.u.qadd(radec0)(station) << Meq.Parm(table_name=self._uvw_table),
            self.ns.v.qadd(radec0)(station) << Meq.Parm(table_name=self._uvw_table),
            self.ns.w.qadd(radec0)(station) << Meq.Parm(table_name=self._uvw_table)
          );
        # else create MeqUVW node to compute them
        else:
          uvw_def = Meq.UVW(radec = radec0,
                            xyz_0 = xyz0,
                            xyz   = xyz(station));
        # do UVW need to be mirrored?
        if self._mirror_uvw:
          uvw(station) << Meq.Negate(self.ns.m_uvw(station) << uvw_def );
        else:
          uvw(station) << uvw_def;
    return uvw(*quals);
  
  def uvw_ifr (self,radec0,*quals):
    """returns interferometer UV node(s) for a given observation.
    If an IFR is supplied, returns UV node for that IFR""";
    uvw_ifr = self.ns.uvw_ifr.qadd(radec0);
    if not uvw_ifr(*(self.ifrs()[0])).initialized():
      uvw = self.uvw(radec0);
      for sta1,sta2 in self.ifrs():
        uvw_ifr(sta1,sta2) << uvw(sta2) - uvw(sta1);
    return uvw_ifr(*quals);
    
  def uv (self,radec0,*quals):
    """returns station UV node(s) for a given phase centre direction.
    If a station is supplied, returns UV node for that station""";
    uv = self.ns.uv.qadd(radec0);
    if not uv(self.stations()[0]).initialized():
      uvw = self.uvw(radec0);
      for station in self.stations():
        uv(station) << Meq.Selector(uvw(station),index=(0,1),multi=True);
    return uv(*quals);

  def uv_ifr (self,radec0,*quals):
    """returns station UV node(s) for a given phase centre direction.
    If a station is supplied, returns UV node for that station""";
    uv_ifr = self.ns.uv_ifr.qadd(radec0);
    if not uv_ifr(*(self.ifrs()[0])).initialized():
      uvw_ifr = self.uvw_ifr(radec0);
      for ifr in self.ifrs():
        uv_ifr(*ifr) << Meq.Selector(uvw_ifr(*ifr),index=(0,1),multi=True);
    return uv_ifr(*quals);
