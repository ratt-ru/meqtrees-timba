from Timba.TDL import *
from Meow.Utils import *
from Meow.Direction import *
from Meow.PointSource import *
from Meow.GaussianSource import *
#from Meow.Shapelet import *

from Timba.LSM.LSM import LSM


def point_and_extended_sources (ns,lsm,tablename=''):
  """ define two extended sources: positions and flux densities """
  parm_options = record(
      use_previous=False,
      table_name=tablename,
      node_groups='Parm');
  

  x00=3826445.09045;
  y00=460923.318101;
  z00=5064346.19305;

  #x00=3.826318521230000e+06;
  #y00=4.609211927340000e+05;
  #z00=5.064441374160000e+06;


  source_model = []

  #plist=lsm.queryLSM(all=1)
  plist=lsm.queryLSM(count=1000)

  for pu in plist:
     (ra,dec,sI,sQ,sU,sV,SIn,f0,RM)=pu.getEssentialParms(ns)
     (eX,eY,eP)=pu.getExtParms()
     # scale 2 difference
     eX=eX*2
     eY=eY*2
     if f0==0:
       f0=150e6
     if eX!=0 or eY!=0 or eP!=0:
         source_model.append( GaussianSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=AEDirection(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP,
                  parm_options=parm_options));
     else:
       # point sources
       if RM==0: 
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=AEDirection(ns,pu.name,ra,dec,x00,y00,z00, parm_options=parm_options),
                  spi=SIn,freq0=f0,
                  parm_options=parm_options));

       else:
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=AEDirection(ns,pu.name,ra,dec,x00,y00,z00,parm_options=parm_options),
                  spi=SIn,freq0=f0, RM=RM,
                  parm_options=parm_options));



  return source_model


### for phase tracking
def point_and_extended_sources_abs (ns,lsm,tablename=''):
  """ define two extended sources: positions and flux densities """
  parm_options = record(
      use_previous=False,
      table_name=tablename,
      node_groups='Parm');
  

  source_model = []

  #plist=lsm.queryLSM(all=1)
  plist=lsm.queryLSM(count=1000)

  for pu in plist:
     (ra,dec,sI,sQ,sU,sV,SIn,f0,RM)=pu.getEssentialParms(ns)
     (eX,eY,eP)=pu.getExtParms()
     # scale 2 difference
     eX=eX*2
     eY=eY*2
     if f0==0:
       f0=150e6
     if eX!=0 or eY!=0 or eP!=0:
         source_model.append( GaussianSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP,
                  parm_options=parm_options));
     else:
       # point sources
       if RM==0: 
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0));

       else:
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0, RM=RM,
                  parm_options=parm_options));



  return source_model



#################### beams beams ...
def makebeam(ns=None,pol='X',station=0,solvable=False,solvables=[],meptable=None):
    p_scale=ns.p_scale(pol,station)
    if not p_scale.initialized():
       p_scale<<Meq.Parm(beam_scale,node_groups='Parm', table_name=meptable,auto_save=True);
    p_phi=ns.p_phi(pol,station)
    if pol=='Y':
      # add extra pi/2 
      if not p_phi.initialized():
        p_phi<<Meq.Parm(beam_phi0+math.pi/2,node_groups='Parm', table_name=meptable,auto_save=True);
    else:
      if not p_phi.initialized():
        p_phi<<Meq.Parm(beam_phi0,node_groups='Parm', table_name=meptable,auto_save=True);
    p_h=ns.p_h(pol,station)
    if not p_h.initialized():
      p_h<<Meq.Parm(beam_h0,node_groups='Parm', table_name=meptable,auto_save=True);

    if solvable:
        solvables.append(p_scale.name);
        solvables.append(p_phi.name);
        solvables.append(p_h.name);

    beam = ns.beam(pol,station) << Meq.PrivateFunction(children =(p_scale,p_phi,p_h),
        lib_name=beam_library_path,function_name="test");

    return beam;

def compute_jones (Jones,sources,pointing_offsets=None,**kw):
  ns = Jones.Subscope();
  # Make dict of per-source, per-station ra-dec nodes.
  # If no pointing errors are passed in, then there's only a per-source node,
  # so the dict will reference it repeatedly for all stations
  radecs = {};
  # incorporate pointings, if needed
  radec0 = Context.observation.phase_centre.radec();
  if pointing_offsets:
    # create nodes to compute actual pointing per source, per antenna
    for p in Context.array.stations():
      for src in sources:
        radecs[src.name,p] = \
          ns.radec(src,p) << Meq.LMRaDec(radec_0=radec0,lm=(
                                ns.lm(src,p) << src.direction.lm() + pointing_offsets(p)));
  else:
    for src in sources:
      radec = ns.radec(src) << Meq.LMRaDec(radec_0=radec0,lm=src.direction.lm());
      for p in Context.array.stations():
        radecs[src.name,p] = radec;
  
  beam_model(Jones,Context.array,radecs,Context.observation.phase_centre.radec());
  
  return Jones;

### BEAM
def EJones (Ej0,array,src_radecs,radec0,meptable=None,solvables=[],solvable=False):
  ns = Ej0.Subscope();
  Bx={}
  By={}
  for station in array.stations():
   Bx[station] = makebeam(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By[station] = makebeam(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for (src,station),src_radec in src_radecs.iteritems():
    # create Az,El per station, per source
    azelnode=ns.azel(src,station)<<Meq.AzEl(radec=src_radec,xyz=xyz(station))
    Xediag = ns.Xediag(src,station) << Meq.Compounder(children=[azelnode,Bx[station]],common_axes=[hiid('l'),hiid('m')])
    Yediag = ns.Yediag(src,station) << Meq.Compounder(children=[azelnode,By[station]],common_axes=[hiid('l'),hiid('m')])
    # create E matrix
    Ej0(src,station) << Meq.Matrix22(Xediag,0,0,Yediag);
    
  return Ej0;


### BEAM with projection -- fast
def EJones_P (Ej0,array,src_radecs,radec0,meptable=None,solvables=[],solvable=False):
  ns = Ej0.Subscope();
  Bx={}
  By={}
  for station in array.stations():
   Bx[station] = makebeam(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By[station] = makebeam(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for (src,station),src_radec in src_radecs.iteritems():
    # create Az,El per station, per source
    azelnode=ns.azel(src,station)<<Meq.AzEl(radec=src_radec,xyz=xyz(station))
    # projection
    az=ns.az(src,station)<<Meq.Selector(azelnode,multi=True,index=[0])
    el=ns.el(src,station)<<Meq.Selector(azelnode,multi=True,index=[1])
    # sin,cosines
    az_C=ns.az_C(src,station)<<Meq.Cos(az);
    az_S=ns.az_S(src,station)<<Meq.Sin(az);
    el_S=ns.el_S(src,station)<<Meq.Sin(el);
    proj=ns.proj(src,station)<<Meq.Matrix22(el_S*az_C,az_S,Meq.Negate(el_S*az_S),az_C);

    Xediag = ns.Xediag(src,station) << Meq.Compounder(children=[azelnode,Bx[station]],common_axes=[hiid('l'),hiid('m')])
    Yediag = ns.Yediag(src,station) << Meq.Compounder(children=[azelnode,By[station]],common_axes=[hiid('l'),hiid('m')])
    # create E matrix
    EE=ns.E0(src,station)<<Meq.Matrix22(Xediag,0,0,Yediag);
    Ej0(src,station) <<Meq.MatrixMultiply(EE,proj)
    
  return Ej0;


TDLCompileOption('beam_model',"Beam model",[EJones,EJones_P]);
TDLCompileOption('beam_library_path',
      "Beam library path",TDLFileSelect("*.so",exist=True,default='beam.so'));
TDLCompileOption('beam_scale',"Beam scale",1.0,more=float);
TDLCompileOption('beam_phi0',"Beam phi0",0,more=float);
TDLCompileOption('beam_h0',"Beam h0",1.4,more=float);


