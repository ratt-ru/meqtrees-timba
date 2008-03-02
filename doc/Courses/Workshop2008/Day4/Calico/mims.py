from Timba.TDL import *
from Meow import Context
import math
import iono_geometry

def center_tecs_only (ns,source_list):
  """Creates MIM to solve for one TEC per station independently.
  Returns Zeta-jones node, which should be qualified with source name 
  and antenna to get a TEC""";

  polc_shape = [polc_deg_time+1,1];
  src0 = source_list[0];
  tecs = ns.tec;
  for p in Context.array.stations():
    tecs(p) << Meq.Parm(tec0,shape=polc_shape,
                   constrain=[.8*tec0,1.2*tec0],
                   tags="mim solvable tec",
                   table_name=get_mep_table());
    
  tecfunc = lambda srcname,p: tecs(p);
  
  return iono_geometry.compute_zeta_jones_from_tecs(ns,tecs,source_list);

  
def per_direction_tecs (ns,source_list):
  """Creates MIM to solve for one TEC per source, per station.
  Returns Zeta-jones node, which should be qualified with source name 
  and antenna to get a TEC""";
  polc_shape = [polc_deg_time+1,1];
  tecs = ns.tec;
  for src in source_list:
    name = src.direction.name;
    for p in Context.array.stations():
      tec = tecs(name,p) << Meq.Parm(tec0,shape=polc_shape,
                            tags="mim solvable tec",
                            constrain=[.8*tec0,1.2*tec0],
                            table_name=get_mep_table());
    
  return iono_geometry.compute_zeta_jones_from_tecs(ns,tecs,source_list);


def mim_poly (ns,source_list,tec0=10.):
  """Creates simple polynomial MIM over the array.
  Returns Zeta-jones node, which should be qualified with source name 
  and antenna to get a TEC""";

  polc_shape = [polc_deg_time+1,1];
  # compute piercing points and zenith angle cosines
  pxy = iono_geometry.compute_piercings(ns,source_list);
  za_cos = iono_geometry.compute_za_cosines(ns,source_list);
  # make MIM parms
  parmlist = [];
  mc = ns.mim_coeff;
  degs = range(mim_polc_degree+1);
  polc_degs = [ (dx,dy) for dx in degs for dy in degs \
                if dx+dy <= mim_polc_degree ];
  for degx,degy in polc_degs:
    if not degx and not degy:
      mc(degx,degy) << Meq.Parm(tec0,shape=polc_shape,
                                table_name=get_mep_table(),
                                tags="mim solvable");
    else:
      mc(degx,degy) << Meq.Parm(0,shape=polc_shape,
                                table_name=get_mep_table(),
                                tags="mim solvable");
  # make TEC subtrees
  tecs = ns.tec;
  for src in source_list:
    name = src.direction.name;
    for p in Context.array.stations():
      # normalized piercing point: divide by 1000km
      npx = ns.npx(name,p) << (ns.px(name,p) << Meq.Selector(pxy(name,p),index=0))*1e-6;
      npy = ns.npy(name,p) << (ns.py(name,p) << Meq.Selector(pxy(name,p),index=1))*1e-6;
      for degx,degy in polc_degs:
        npxypow = ns.npxypow(name,p,degx,degy) << Meq.Pow(npx,degx)*Meq.Pow(npy,degy);
        ns.vtecs(name,p,degx,degy) << mc(degx,degy)*npxypow;
      ns.vtec(name,p) << Meq.Add(*[ns.vtecs(name,p,dx,dy) for dx,dy in polc_degs]);
      tecs(name,p) << Meq.Divide(ns.vtec(name,p),za_cos(name,p),tags="mim tec");

  return iono_geometry.compute_zeta_jones_from_tecs(ns,tecs,source_list);

def compute_jones (Jones,sources,stations=None,inspectors=[],label='Z',**kw):
  """Creates the Z Jones for ionospheric phase, given TECs (per source, 
  per station).""";
  stations = stations or Context.array.stations;
  ns = Jones.Subscope();
  piercings = iono_geometry.compute_piercings(ns,sources,stations);
  za_cos = iono_geometry.compute_za_cosines(ns,sources,stations);
  tecs = iono_model(ns,piercings,za_cos,sources,stations);
  # make inspector for TECs
  inspectors.append(
    Jones.scope.inspector('TEC') << StdTrees.define_inspector(tecs,sources,stations,
                                                   label='tec',freqavg=False)
  );
  iono_geometry.compute_zeta_jones_from_tecs(Jones,tecs,sources,stations);
  
  # make inspector for ionospheric phases
  Zphase = ns.Zphase;
  for src in sources:
    for p in stations:
      Zphase(src,p) << Meq.Arg(Jones(src,p));
  inspectors.append(
    Jones.scope.inspector('iono_phase') << \
        StdTrees.define_inspector(Zphase,sources,stations,label='z')
  );
  
  # make parmgroups for TEC paramaters
  global _pg_mim;
  _pg_mim  = ParmGroup.ParmGroup(label+"_mim",
             Jones.search(tags="mim solvable"),
             table_name="%s_mim.mep"%label,bookmark=False);

  # make solvejobs
  ParmGroup.SolveJob("cal_"+label+"_mim","Calibrate %s (MIM)"%label,_pg_mim);

  return Jones;

TDLCompileMenu('MIM options',
  TDLOption("iono_model","Ionospheric model",
              [ mims.mim_poly,
                mims.center_tecs_only,
                mims.per_direction_tecs,
              ]),
  TDLOption('mim_polc_degree',"Polc degree in X/Y",[1,2,3,4],more=int),
  TDLOption('polc_deg_time',"Polc degree, in time",[0,1,2],more=int),
  TDLOption('tec0',"Base TEC value",[0,1,5,10],more=float)
);
