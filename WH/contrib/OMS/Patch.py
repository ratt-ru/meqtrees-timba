from Timba.Contrib.OMS.SkyComponent import *


class Patch (SkyComponent):
  def __init__(self,ns,name,ra=0.0,dec=0.0,
               parm_options=record(node_groups='Parm')):
    SkyComponent.__init__(self,ns,name,ra,dec,parm_options=parm_options);
    self._components = [];
    
  def add (self,*comps):
    """adds components to patch""";
    self._components += comps;
    
  def make_clean_visibilities (self,visnode,array,observation):
    """Creates predicted visibility for patch.""";
    # no components -- use 0
    if not self._components:
      [ visnode(sta1,sta2) << 0.0 for sta1,sta2 in array.ifrs() ];
    # 1 component -- use that visibility directly
    elif len(self._components) == 1:
      self._components[0].make_clean_visibilities(visnode,array,observation);
    else:
      # work out component visibilities
      compvis = [comp.visibility(array,observation) for comp in self._components];
      # add them up per-ifr
      [ visnode(sta1,sta2) << Meq.Add(*[vis(sta1,sta2) for vis in compvis])
        for sta1,sta2 in array.ifrs()
      ];
    pass;
  
