from Timba.TDL import *
from Meow.Utils import *
from Meow.Direction import *
from Meow.ODirection import *
from Meow.PointSource import *
from Meow.GaussianSource import *
from Meow.DiskSource import *

import Meow
from Meow.Shapelet import *

from Timba.LSM.LSM import LSM


beampath="/home/sarod/";
## for observations without phase tracking
def point_and_extended_sources_nophasetrack(ns,lsm,tablename=''):
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
         #source_model.append( GaussianSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
         #         Iorder=0, direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
         #         spi=SIn,freq0=f0,
         #         size=[eX,eY],phi=eP,
         #         parm_options=parm_options));
         source_model.append( Shapelet(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP,
                  modefile=beampath+"/Cas_A-4.model.FITS.modes"));
     else:
       # point sources
       if RM==0: 
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0));

       else:
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0, RM=RM,
                  ));



  return source_model

### for solvable fluxes
def point_and_extended_sources_solvable(ns,lsm,tablename=''):
  """ define two extended sources: positions and flux densities """
  parm_options = record(
      use_previous=False,
      table_name=tablename,
      node_groups='Parm');
  

  source_model = []

  #plist=lsm.queryLSM(all=1)
  plist=lsm.queryLSM(count=30)

  for pu in plist:
     (ra,dec,sI,sQ,sU,sV,SIn,f0,RM)=pu.getEssentialParms(ns)
     (eX,eY,eP)=pu.getExtParms()
     # scale 2 difference
     eX=eX*2
     eY=eY*2
     if f0==0:
       f0=150e6
     if eX!=0 or eY!=0 or eP!=0:
         source_model.append( GaussianSource(ns,name=pu.name,I=Meow.Parm(sI), Q=Meow.Parm(sQ), U=Meow.Parm(sU), V=Meow.Parm(sV),
                  Iorder=0, direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP,
                  parm_options=parm_options));
     else:
       # point sources
       if RM==0: 
         source_model.append( PointSource(ns,name=pu.name,I=Meow.Parm(sI), Q=Meow.Parm(sQ), U=Meow.Parm(sU), V=Meow.Parm(sV),
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0));

       else:
         source_model.append( PointSource(ns,name=pu.name,I=Meow.Parm(sI), Q=Meow.Parm(sQ), U=Meow.Parm(sU), V=Meow.Parm(sV),
                  direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0, RM=RM,
                  parm_options=parm_options));



  return source_model

### for phase tracking
def point_and_extended_sources_sun(ns,lsm,tablename=''):
  parm_options = record(
      use_previous=False,
      table_name=tablename,
      node_groups='Parm');
  

  source_model = []

  #plist=lsm.queryLSM(all=1)
  plist=lsm.queryLSM(count=30)

  for pu in plist:
     (ra,dec,sI,sQ,sU,sV,SIn,f0,RM)=pu.getEssentialParms(ns)
     (eX,eY,eP)=pu.getExtParms()
     # scale 2 difference
     eX=eX*2
     eY=eY*2
     if f0==0:
       f0=150e6
     if eX!=0 or eY!=0 or eP!=0:
         #source_model.append( GaussianSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
         #         Iorder=0, direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
         #         spi=SIn,freq0=f0,
         #         size=[eX,eY],phi=eP,
         #         parm_options=parm_options));
         if pu.name=="SUN":
              eX=0.09
              eY=0.09
              source_model.append( DiskSource(ns,name=pu.name,I=Meow.Parm(sI), Q=Meow.Parm(sQ), U=Meow.Parm(sU), V=Meow.Parm(sV),
                   direction=ODirection(ns,pu.name,pu.name),
                   spi=SIn,freq0=f0,
                   size=[eX,eY],phi=eP,
                   ));
         elif pu.name=="DC10":
              eX=0.054
              eY=0.054
              source_model.append( DiskSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                   direction=Direction(ns,pu.name,ra,dec),
                   spi=SIn,freq0=f0,
                   size=[eX,eY],phi=eP,
                   ));
         else:
            source_model.append( Shapelet(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP,
                  modefile=beampath+"/Cas_A-4.model.FITS.modes"));
     else:
       # point sources
       if RM==0: 
         if pu.name=="SUN":
              eX=0.09
              eY=0.09
              source_model.append( DiskSource(ns,name=pu.name,I=Meow.Parm(sI), Q=Meow.Parm(sQ), U=Meow.Parm(sU), V=Meow.Parm(sV),
                   direction=ODirection(ns,pu.name,pu.name),
                   spi=SIn,freq0=f0,
                   size=[eX,eY],phi=eP,
                   ));
         elif pu.name=="DC10":
              eX=0.064
              eY=0.064
              source_model.append( DiskSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                   direction=Direction(ns,pu.name,ra,dec),
                   spi=SIn,freq0=f0,
                   size=[eX,eY],phi=eP,
                   ));
         else:
              source_model.append( PointSource(ns,name=pu.name,I=Meow.Parm(sI), Q=Meow.Parm(sQ), U=Meow.Parm(sU), V=Meow.Parm(sV),
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0));


       else:
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0, RM=RM,
                  ));



  return source_model



def makebeam_droopy_phi(ns=None,pol='X',L=0.9758, phi0=0, alpha=math.pi/4.001, h=1.706, station=0,solvable=False,solvables=[],meptable=None):
    p_L=ns.p_L(pol,station)
    if not p_L.initialized():
       p_L<<Meq.ToComplex(Meq.Parm(L,node_groups='Parm', table_name=meptable,auto_save=True),0);
    p_phi=ns.p_phi(pol,station)
    if pol=='Y':
      # add extra pi/2 
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0-math.pi/2,node_groups='Parm', table_name=meptable,auto_save=True),0);
    else:
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0,node_groups='Parm', table_name=meptable,auto_save=True),0);
    p_h=ns.p_h(pol,station)
    if not p_h.initialized():
      p_h<<Meq.ToComplex(Meq.Parm(h,node_groups='Parm', table_name=meptable,auto_save=True),0);
    p_alpha=ns.p_alpha(pol,station)
    if not p_alpha.initialized():
      p_alpha<<Meq.ToComplex(Meq.Parm(alpha,node_groups='Parm', table_name=meptable,auto_save=True),0);

    if solvable:
        solvables.append(p_L.name);
        solvables.append(p_phi.name);
        solvables.append(p_h.name);
        solvables.append(p_alpha.name);
    beam =  ns.beam_phi(pol,station)<< Meq.PrivateFunction(children =(p_h,p_L,p_alpha,p_phi),
        lib_name=beampath+"/beams/beam_dr_phi.so",function_name="test");

    return beam;

def makebeam_droopy_theta(ns=None,pol='X',L=0.9758, phi0=0, alpha=math.pi/4.001, h=1.706, station=0,solvable=False,solvables=[],meptable=None):
    p_L=ns.p_L(pol,station)
    if not p_L.initialized():
       p_L<<Meq.ToComplex(Meq.Parm(L,node_groups='Parm', table_name=meptable,auto_save=True));
    p_phi=ns.p_phi(pol,station)
    if pol=='Y':
      # add extra pi/2 
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0-math.pi/2,node_groups='Parm', table_name=meptable,auto_save=True));
    else:
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0,node_groups='Parm', table_name=meptable,auto_save=True));
    p_h=ns.p_h(pol,station)
    if not p_h.initialized():
      p_h<<Meq.ToComplex(Meq.Parm(h,node_groups='Parm', table_name=meptable,auto_save=True));
    p_alpha=ns.p_alpha(pol,station)
    if not p_alpha.initialized():
      p_alpha<<Meq.ToComplex(Meq.Parm(alpha,node_groups='Parm', table_name=meptable,auto_save=True));

    if solvable:
        solvables.append(p_L.name);
        solvables.append(p_phi.name);
        solvables.append(p_h.name);
        solvables.append(p_alpha.name);
    beam = ns.beam_theta(pol,station) << Meq.PrivateFunction(children =(p_h,p_L,p_alpha,p_phi),
        lib_name=beampath+"/beams/beam_dr_theta.so",function_name="test");
    return beam;


### the parms here are ignored
def makebeam_hba_phi(ns=None,pol='X',L=0.9758, phi0=0, alpha=math.pi/4.001, h=1.706, station=0,solvable=False,solvables=[],meptable=None):
    p_L=ns.p_L(pol,station)
    if not p_L.initialized():
       p_L<<Meq.ToComplex(Meq.Parm(L,node_groups='Parm', table_name=meptable,auto_save=True),0);
    p_phi=ns.p_phi(pol,station)
    if pol=='Y':
      # add extra pi/2 
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0-math.pi/2,node_groups='Parm', table_name=meptable,auto_save=True),0);
    else:
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0,node_groups='Parm', table_name=meptable,auto_save=True),0);
    p_h=ns.p_h(pol,station)
    if not p_h.initialized():
      p_h<<Meq.ToComplex(Meq.Parm(h,node_groups='Parm', table_name=meptable,auto_save=True),0);
    p_alpha=ns.p_alpha(pol,station)
    if not p_alpha.initialized():
      p_alpha<<Meq.ToComplex(Meq.Parm(alpha,node_groups='Parm', table_name=meptable,auto_save=True),0);

    if solvable:
        solvables.append(p_L.name);
        solvables.append(p_phi.name);
        solvables.append(p_h.name);
        solvables.append(p_alpha.name);
    beam =  ns.beam_phi(pol,station)<< Meq.PrivateFunction(children =(p_h,p_L,p_alpha,p_phi),
        lib_name=beampath+"/beams/hba_beam_phi.so",function_name="test");

    return beam;

def makebeam_hba_theta(ns=None,pol='X',L=0.9758, phi0=0, alpha=math.pi/4.001, h=1.706, station=0,solvable=False,solvables=[],meptable=None):
    p_L=ns.p_L(pol,station)
    if not p_L.initialized():
       p_L<<Meq.ToComplex(Meq.Parm(L,node_groups='Parm', table_name=meptable,auto_save=True));
    p_phi=ns.p_phi(pol,station)
    if pol=='Y':
      # add extra pi/2 
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0-math.pi/2,node_groups='Parm', table_name=meptable,auto_save=True));
    else:
      if not p_phi.initialized():
        p_phi<<Meq.ToComplex(Meq.Parm(phi0,node_groups='Parm', table_name=meptable,auto_save=True));
    p_h=ns.p_h(pol,station)
    if not p_h.initialized():
      p_h<<Meq.ToComplex(Meq.Parm(h,node_groups='Parm', table_name=meptable,auto_save=True));
    p_alpha=ns.p_alpha(pol,station)
    if not p_alpha.initialized():
      p_alpha<<Meq.ToComplex(Meq.Parm(alpha,node_groups='Parm', table_name=meptable,auto_save=True));

    if solvable:
        solvables.append(p_L.name);
        solvables.append(p_phi.name);
        solvables.append(p_h.name);
        solvables.append(p_alpha.name);
    beam = ns.beam_theta(pol,station) << Meq.PrivateFunction(children =(p_h,p_L,p_alpha,p_phi),
        lib_name=beampath+"/beams/hba_beam_theta.so",function_name="test");
    return beam;



#### even more complex droopy dipole
def EJones_droopy_comp(ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E",rotate=False):
  Bx_phi={}
  Bx_theta={}
  By_phi={}
  By_theta={}
  
  # dipole rotations (in degrees)
  diprot=[0,0,0,0,0,22.5,45,67.5,15,37.5,60,82.5,7.5,30,52.5,75];
  dipnum=0;

  for station in array.stations():
   if rotate:
    myphi0=diprot[dipnum]*math.pi/180;
    dipnum=dipnum+1;
   else:
    myphi0=0

   Bx_phi[station] = makebeam_droopy_phi(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables,phi0=myphi0);
   Bx_theta[station] = makebeam_droopy_theta(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables,phi0=myphi0);
   By_phi[station] = makebeam_droopy_phi(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables,phi0=myphi0);
   By_theta[station] = makebeam_droopy_theta(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables,phi0=myphi0);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    # make shifts
    az=ns.az(dirname)<<Meq.Selector(azelnode,multi=True,index=[0])
    azX=ns.azX(dirname)<<az-math.pi/4
    azY=ns.azY(dirname)<<az-math.pi/4
    el=ns.el(dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
   
    # sin,cosines
    #az_CX=ns.az_CX(dirname)<<Meq.Cos(az);
    #az_SX=ns.az_SX(dirname)<<Meq.Sin(az);
    #az_CY=ns.az_CY(dirname)<<Meq.Cos(az);
    #az_SY=ns.az_SY(dirname)<<Meq.Sin(az);
    #el_S=ns.el_S(dirname)<<Meq.Sin(el);

    for station in array.stations():
        Xediag_phi = ns.Xediag_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(azX,el),Bx_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Xediag_theta= ns.Xediag_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(azX,el),Bx_theta[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_phi = ns.Yediag_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(azY,el),By_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_theta = ns.Yediag_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(azY,el),By_theta[station]],common_axes=[hiid('l'),hiid('m')])
        # create E matrix
        Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)/88.0

  return Ej0;


#### even more complex droopy dipole - with station beam
def EJones_droopy_comp_stat(ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx_phi={}
  Bx_theta={}
  By_phi={}
  By_theta={}
  
  for station in array.stations():
   Bx_phi[station] = makebeam_droopy_phi(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   Bx_theta[station] = makebeam_droopy_theta(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_phi[station] = makebeam_droopy_phi(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_theta[station] = makebeam_droopy_theta(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # station beam
  if not ns.freq0.initialized():
    ns.freq0<<Meq.Constant(59e6)
  if not ns.freq1.initialized():
    ns.freq1<<Meq.Constant(60e6)

  if not ns.Xstatbeam.initialized():
    Xstatbeam=ns.Xstatbeam<<Meq.StationBeam(filename="AntennaCoords",radec=radec0,xyz=array.xyz0(),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)
  else:
    Xstatbeam=ns.Xstatbeam;

  if not ns.Ystatbeam.initialized():
   Ystatbeam=ns.Ystatbeam<<Meq.StationBeam(filename="AntennaCoords",radec=radec0,xyz=array.xyz0(),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)
  else:
    Ystatbeam=ns.Ystatbeam;

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    # make shifts
    az=ns.az(dirname)<<Meq.Selector(azelnode,multi=True,index=[0])
    azX=ns.azX(dirname)<<az-math.pi/4
    azY=ns.azY(dirname)<<az-math.pi/4
    el=ns.el(dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
   

    for station in array.stations():
        azelX =ns.azelX(dirname,station)<<Meq.Composer(azX,el)
        azelY =ns.azelY(dirname,station)<<Meq.Composer(azY,el)
        Xediag_phi = ns.Xediag_phi(dirname,station) << Meq.Compounder(children=[azelX,Bx_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Xediag_theta= ns.Xediag_theta(dirname,station) << Meq.Compounder(children=[azelX,Bx_theta[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_phi = ns.Yediag_phi(dirname,station) << Meq.Compounder(children=[azelY,By_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_theta = ns.Yediag_theta(dirname,station) << Meq.Compounder(children=[azelY,By_theta[station]],common_axes=[hiid('l'),hiid('m')])
        # create E matrix, normalize for zenith at 60MHz
        #Ej(station) <<Meq.Matrix22(el_S*az_CX*Xediag_theta,az_SX*Xediag_phi,Meq.Negate(el_S*az_SY)*Yediag_theta,az_CY*Yediag_phi)
        if station==1:
          Xstatgain=ns.Xstatgain(dirname,station)<<Meq.Compounder(children=[azelX,Xstatbeam],common_axes=[hiid('l'),hiid('m')])
          Ystatgain=ns.Ystatgain(dirname,station)<<Meq.Compounder(children=[azelY,Ystatbeam],common_axes=[hiid('l'),hiid('m')])
          Ej(station) <<Meq.Matrix22(Xstatgain*Xediag_theta,Xstatgain*Xediag_phi,Ystatgain*Yediag_theta,Ystatgain*Yediag_phi)/88.00
          #Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)
        else:
          Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)/88.00
        #Ej(station) <<Meq.Matrix22(el_S*az_S*Xediag_theta,az_C*Xediag_phi,Meq.Negate(el_S*az_S)*Yediag_theta,az_C*Yediag_phi)

  return Ej0;


#### HBA
def EJones_HBA(ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx_phi={}
  Bx_theta={}
  By_phi={}
  By_theta={}
  
  for station in array.stations():
   Bx_phi[station] = makebeam_hba_phi(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   Bx_theta[station] = makebeam_hba_theta(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_phi[station] = makebeam_hba_phi(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_theta[station] = makebeam_hba_theta(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    # make shifts
    az=ns.az(dirname)<<Meq.Selector(azelnode,multi=True,index=[0])
    azX=ns.azX(dirname)<<az-math.pi/4
    azY=ns.azY(dirname)<<az-math.pi/4
    el=ns.el(dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
   
    for station in array.stations():
        Xediag_phi = ns.Xediag_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(azX,el),Bx_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Xediag_theta= ns.Xediag_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(azX,el),Bx_theta[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_phi = ns.Yediag_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(azY,el),By_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_theta = ns.Yediag_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(azY,el),By_theta[station]],common_axes=[hiid('l'),hiid('m')])
        # create E matrix
        Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)/600.00

  return Ej0;

def EJones_HBA_stat0(ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx_phi={}
  Bx_theta={}
  By_phi={}
  By_theta={}
  
  ## wich ones are beamformed
  beam_formed=[3,4]
 
  for station in array.stations():
   Bx_phi[station] = makebeam_hba_phi(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   Bx_theta[station] = makebeam_hba_theta(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_phi[station] = makebeam_hba_phi(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_theta[station] = makebeam_hba_theta(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # station beam
  if not ns.freq0.initialized():
    ns.freq0<<Meq.Constant(159e6)
  if not ns.freq1.initialized():
    ns.freq1<<Meq.Constant(160e6)


  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    # make shifts
    az=ns.az(dirname)<<Meq.Selector(azelnode,multi=True,index=[0])
    azX=ns.azX(dirname)<<az-math.pi/4
    azY=ns.azY(dirname)<<az-math.pi/4
    el=ns.el(dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
   

    for station in array.stations():
        azelX =ns.azelX(dirname,station)<<Meq.Composer(azX,el)
        azelY =ns.azelY(dirname,station)<<Meq.Composer(azY,el)
        Xediag_phi = ns.Xediag_phi(dirname,station) << Meq.Compounder(children=[azelX,Bx_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Xediag_theta= ns.Xediag_theta(dirname,station) << Meq.Compounder(children=[azelX,Bx_theta[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_phi = ns.Yediag_phi(dirname,station) << Meq.Compounder(children=[azelY,By_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_theta = ns.Yediag_theta(dirname,station) << Meq.Compounder(children=[azelY,By_theta[station]],common_axes=[hiid('l'),hiid('m')])
        if station in beam_formed:
          Xstatbeam=ns.Xstatbeam(dirname,station)<<Meq.StationBeam(filename=beampath+'/beams/AntennaCoords',radec=radec0,xyz=xyz(station),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)
          Ystatbeam=ns.Ystatbeam(dirname,station)<<Meq.StationBeam(filename=beampath+'/beams/AntennaCoords',radec=radec0,xyz=xyz(station),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)

          Xstatgain=ns.Xstatgain(dirname,station)<<Meq.Compounder(children=[azelX,Xstatbeam],common_axes=[hiid('l'),hiid('m')])
          Ystatgain=ns.Ystatgain(dirname,station)<<Meq.Compounder(children=[azelY,Ystatbeam],common_axes=[hiid('l'),hiid('m')])
          Ej(station) <<Meq.Matrix22(Xstatgain*Xediag_theta,Xstatgain*Xediag_phi,Ystatgain*Yediag_theta,Ystatgain*Yediag_phi)/600.00
          #Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)
        else:
          Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)/600.00
        #Ej(station) <<Meq.Matrix22(el_S*az_S*Xediag_theta,az_C*Xediag_phi,Meq.Negate(el_S*az_S)*Yediag_theta,az_C*Yediag_phi)

  return Ej0;

def EJones_HBA_stat(ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx_phi={}
  Bx_theta={}
  By_phi={}
  By_theta={}
  
  ## wich ones are beamformed
  beam_formed=[9,10,11,12]
 
  for station in array.stations():
   Bx_phi[station] = makebeam_hba_phi(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   Bx_theta[station] = makebeam_hba_theta(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_phi[station] = makebeam_hba_phi(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By_theta[station] = makebeam_hba_theta(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # station beam
  if not ns.freq0.initialized():
    ns.freq0<<Meq.Constant(159e6)
  if not ns.freq1.initialized():
    ns.freq1<<Meq.Constant(160e6)


  ### dummy xyz for beamformer
  #x00=10000; y00=100000; z00=100;
  #x00=3818797.786607182; y00=5051723.325381768; z00=757842.9797027396;
  #if not ns.xyz_dummy.initialized():
  #  ns.xyz_dummy<<Meq.Composer(x00,y00,z00)
  ### track zenith
  #az00=math.pi; el00=math.pi/2;
  #if not ns.radec_dummy.initialized():
  #  radec00=ns.radec_dummy<<Meq.Mean(Meq.RADec(Meq.Composer(az00,el00),xyz(5)))

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    # make shifts
    az=ns.az(dirname)<<Meq.Selector(azelnode,multi=True,index=[0])
    azX=ns.azX(dirname)<<az-math.pi/4
    azY=ns.azY(dirname)<<az-math.pi/4
    el=ns.el(dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
   

    for station in array.stations():
        azelX =ns.azelX(dirname,station)<<Meq.Composer(azX,el)
        azelY =ns.azelY(dirname,station)<<Meq.Composer(azY,el)
        Xediag_phi = ns.Xediag_phi(dirname,station) << Meq.Compounder(children=[azelX,Bx_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Xediag_theta= ns.Xediag_theta(dirname,station) << Meq.Compounder(children=[azelX,Bx_theta[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_phi = ns.Yediag_phi(dirname,station) << Meq.Compounder(children=[azelY,By_phi[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag_theta = ns.Yediag_theta(dirname,station) << Meq.Compounder(children=[azelY,By_theta[station]],common_axes=[hiid('l'),hiid('m')])
        if station in beam_formed:
          Xstatbeam=ns.Xstatbeam(dirname,station)<<Meq.StationBeam(filename=beampath+'/beams/AntennaCoords',radec=radec0,xyz=xyz(station),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)
          #radec00=ns.radec_dummy(dirname,station,'x')<<Meq.RADec(Meq.Composer(az00,el00),xyz(station))

          #Xstatbeam=ns.Xstatbeam(dirname,station)<<Meq.StationBeam(filename=beampath+'/beams/AntennaCoords',radec=radec00,xyz=xyz(station),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)
          Ystatbeam=ns.Ystatbeam(dirname,station)<<Meq.StationBeam(filename=beampath+'/beams/AntennaCoords',radec=radec0,xyz=xyz(station),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)

          #radec00=ns.radec_dummy(dirname,station,'y')<<Meq.RADec(Meq.Composer(az00,el00),xyz(station))
          #Ystatbeam=ns.Ystatbeam(dirname,station)<<Meq.StationBeam(filename=beampath+'/beams/AntennaCoords',radec=radec00,xyz=xyz(station),phi0=Meq.Constant(-math.pi/4),ref_freq=(ns.freq0+ns.freq1)/2)

          Xstatgain=ns.Xstatgain(dirname,station)<<Meq.Compounder(children=[azelX,Xstatbeam],common_axes=[hiid('l'),hiid('m')])
          Ystatgain=ns.Ystatgain(dirname,station)<<Meq.Compounder(children=[azelY,Ystatbeam],common_axes=[hiid('l'),hiid('m')])
          Ej(station) <<Meq.Matrix22(Xstatgain*Xediag_theta,Xstatgain*Xediag_phi,Ystatgain*Yediag_theta,Ystatgain*Yediag_phi)/600.00
          #Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)
        else:
          Ej(station) <<Meq.Matrix22(Xediag_theta,Xediag_phi,Yediag_theta,Yediag_phi)/600.00
        #Ej(station) <<Meq.Matrix22(el_S*az_S*Xediag_theta,az_C*Xediag_phi,Meq.Negate(el_S*az_S)*Yediag_theta,az_C*Yediag_phi)

  return Ej0;






##### beam using FITS file
def EJones_fits(ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E",lba=True,rotate=False):
  if lba:
    ns.theta_real<< Meq.FITSImage(filename=beampath+'/beams/lba_beam_theta_real.fits',cutoff=1.0,mode=2)
    ns.theta_imag<< Meq.FITSImage(filename=beampath+'/beams/lba_beam_theta_imag.fits',cutoff=1.0,mode=2)
    ns.phi_real<< Meq.FITSImage(filename=beampath+'/beams/lba_beam_phi_real.fits',cutoff=1.0,mode=2)
    ns.phi_imag<< Meq.FITSImage(filename=beampath+'/beams/lba_beam_phi_imag.fits',cutoff=1.0,mode=2)
  else:
    ns.theta_real<< Meq.FITSImage(filename=beampath+'/beams/hba_beam_theta_real.fits',cutoff=1.0,mode=2)
    ns.theta_imag<< Meq.FITSImage(filename=beampath+'/beams/hba_beam_theta_imag.fits',cutoff=1.0,mode=2)
    ns.phi_real<< Meq.FITSImage(filename=beampath+'/beams/hba_beam_phi_real.fits',cutoff=1.0,mode=2)
    ns.phi_imag<< Meq.FITSImage(filename=beampath+'/beams/hba_beam_phi_imag.fits',cutoff=1.0,mode=2)
 
  beam_phi=ns.resampler_phi << Meq.Resampler(Meq.ToComplex(ns.phi_real,ns.phi_imag), dep_mask=0xff)
  beam_theta=ns.resampler_theta<< Meq.Resampler(Meq.ToComplex(ns.theta_real,ns.theta_imag), dep_mask=0xff)

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # dipole rotations (in degrees)
  diprot=[0,0,0,0,0,22.5,45,67.5,15,37.5,60,82.5,7.5,30,52.5,75];


  # create per-direction, per-station E Jones matrices
  for src in sources:

    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);
    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    dipnum=0;
    for station in array.stations():
        if rotate:
          myphi0=diprot[dipnum]*math.pi/180-math.pi/4;
          dipnum=dipnum+1;
        else:
          myphi0=-math.pi/4


        # make shifts
        az=ns.az(station,dirname)<<Meq.Selector(azelnode,multi=True,index=[0])+myphi0
        el0=ns.el0(station,dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
        theta=ns.theta(station,dirname)<<-el0+math.pi/2
        # find modulo values add 20 deg to fit to right grid points
        az_X=ns.az_X(station,dirname)<<az-Meq.Floor(az/(2*math.pi))*2*math.pi+math.pi/9
        az_y=ns.az_y(station,dirname)<<az_X-math.pi/2
        az_Y=ns.az_Y(station,dirname)<<az_y-Meq.Floor(az_y/(2*math.pi))*2*math.pi


        X_theta = ns.X_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_X,theta),beam_theta],common_axes=[hiid('l'),hiid('m')])
        X_phi= ns.X_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_X,theta),beam_phi],common_axes=[hiid('l'),hiid('m')])
        Y_theta = ns.Y_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_Y,theta),beam_theta],common_axes=[hiid('l'),hiid('m')])
        Y_phi= ns.Y_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_Y,theta),beam_phi],common_axes=[hiid('l'),hiid('m')])
        Ej(station) <<Meq.Matrix22(X_theta,X_phi,Y_theta,Y_phi)

  return Ej0;



################# shapelet beam
def setup_shapelet(ns,modefile,qual=''):
    # read mode file
    infile=open(modefile,'r');
    all=infile.readlines()
    infile.close()
    thisline=all[0].split()
    n0=int(thisline[0]);
    beta=float(thisline[1]);
    _children=[];
    _children+=[ns.parm('beta'+qual+str(n0))<<Meq.Parm(beta,tags='beta')];
    for ci in range(1,n0+1):
      thisline=all[ci].split()
      modeval_r=float(thisline[0])
      modeval_i=float(thisline[1])
      _children+=[ns.parm(str(ci)+qual)<<Meq.ToComplex(Meq.Parm(modeval_r,tags='modes'), Meq.Parm(modeval_i,tags='modes'))];

    clist=ns.clist(qual)<<Meq.Composer(children=_children)
    shptf= ns.beam(qual)
    if not shptf.initialized():
      shptf= ns.beam(qual)<<Meq.ShapeletVisTf(modes=clist,method=1,dep_mask=0xff);
    return shptf

def EJones_shapelet(ns,array,sources,radec0,name="E",rotate=False):
  Bx_phi={}
  Bx_theta={}
  By_phi={}
  By_theta={}
  
  # dipole rotations (in degrees)
  diprot=[0,0,0,0,0,22.5,45,67.5,15,37.5,60,82.5,7.5,30,52.5,75];
  dipnum=0;

  for station in array.stations():
   if rotate:
    myphi0=diprot[dipnum]*math.pi/180;
    dipnum=dipnum+1;
   else:
    myphi0=0

  ## cutoff below horizon
  beamc = ns.beamc(name)
  if not beamc.initialized():
     beamc = ns.beamc(name) << Meq.Mean(Meq.PrivateFunction(
          lib_name=beampath+"/beams/beam_cutoff.so",function_name="test"));


  B_theta=setup_shapelet(ns(name),beampath+'/beams/polar_theta_lba_40.modes',qual='theta_polar')
  B_phi=setup_shapelet(ns(name),beampath+'/beams/polar_phi_lba_40.modes',qual='phi_polar')
  beam_theta=B_theta*beamc
  beam_phi=B_phi*beamc

  Ej0 = ns[name];
  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for src in sources:

    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);
    # create Az,El per source, using station 1
    azelnode=ns.azel(dirname)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(1))
    dipnum=0;
    for station in array.stations():
        if rotate:
          myphi0=diprot[dipnum]*math.pi/180-math.pi/4;
          dipnum=dipnum+1;
        else:
          myphi0=-math.pi/4


        # make shifts
        az=ns.az(station,dirname)<<Meq.Selector(azelnode,multi=True,index=[0])+myphi0
        el0=ns.el0(station,dirname)<<Meq.Selector(azelnode,multi=True,index=[1])
        theta=ns.theta(station,dirname)<<-el0+math.pi/2
        az_X=ns.az_X(station,dirname)<<az-Meq.Floor(az/(2*math.pi))*2*math.pi
        az_y=ns.az_y(station,dirname)<<az_X-math.pi/2
        az_Y=ns.az_Y(station,dirname)<<az_y-Meq.Floor(az_y/(2*math.pi))*2*math.pi


        X_theta = ns.X_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_X,theta),beam_theta],common_axes=[hiid('l'),hiid('m')])
        X_phi= ns.X_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_X,theta),beam_phi],common_axes=[hiid('l'),hiid('m')])
        Y_theta = ns.Y_theta(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_Y,theta),beam_theta],common_axes=[hiid('l'),hiid('m')])
        Y_phi= ns.Y_phi(dirname,station) << Meq.Compounder(children=[Meq.Composer(az_Y,theta),beam_phi],common_axes=[hiid('l'),hiid('m')])
        Ej(station) <<Meq.Matrix22(X_theta,X_phi,Y_theta,Y_phi)


  return Ej0;
