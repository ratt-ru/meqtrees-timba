#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Meow.Utils import *
from Meow.AEDirection import *
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
def makebeam(ns=None,pol='X',scale=1.0, phi0=0, h0=1.4, station=0,solvable=False,solvables=[],meptable=None):
    p_scale=ns.p_scale(pol,station)
    if not p_scale.initialized():
       p_scale<<Meq.Parm(scale,node_groups='Parm', table_name=meptable,auto_save=True);
    p_phi=ns.p_phi(pol,station)
    if pol=='Y':
      # add extra pi/2 
      if not p_phi.initialized():
        p_phi<<Meq.Parm(phi0+math.pi/2,node_groups='Parm', table_name=meptable,auto_save=True);
    else:
      if not p_phi.initialized():
        p_phi<<Meq.Parm(phi0,node_groups='Parm', table_name=meptable,auto_save=True);
    p_h=ns.p_h(pol,station)
    if not p_h.initialized():
      p_h<<Meq.Parm(h0,node_groups='Parm', table_name=meptable,auto_save=True);

    if solvable:
        solvables.append(p_scale.name);
        solvables.append(p_phi.name);
        solvables.append(p_h.name);

    beam = ns.beam(pol,station) << Meq.PrivateFunction(children =(p_scale,p_phi,p_h),
        lib_name="./beams/beam.so",function_name="test");

    return beam;

### BEAM
def EJones (ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx={}
  By={}
  for station in array.stations():
   Bx[station] = makebeam(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By[station] = makebeam(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    for station in array.stations():
        # create Az,El per station, per source
        azelnode=ns.azel(dirname,station)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(station))
        Xediag = ns.Xediag(dirname,station) << Meq.Compounder(children=[azelnode,Bx[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag = ns.Yediag(dirname,station) << Meq.Compounder(children=[azelnode,By[station]],common_axes=[hiid('l'),hiid('m')])
        # create E matrix
        Ej(station) << Meq.Matrix22(Xediag,0,0,Yediag);
  return Ej0;

### BEAM with projection -- slow
def EJones_P_old (ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx={}
  By={}
  for station in array.stations():
   Bx[station] = makebeam(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By[station] = makebeam(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    for station in array.stations():
        # create Az,El per station, per source
        azelnode=ns.azel(dirname,station)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(station))
        # projection
        proj=ns.proj(dirname,station)<<Meq.ParAngleL(radec=src.direction.radec(),xyz=xyz(station))

        Xediag = ns.Xediag(dirname,station) << Meq.Compounder(children=[azelnode,Bx[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag = ns.Yediag(dirname,station) << Meq.Compounder(children=[azelnode,By[station]],common_axes=[hiid('l'),hiid('m')])
        # create E matrix
        EE=ns.E0(dirname,station)<<Meq.Matrix22(Xediag,0,0,Yediag);
        Ej(station) <<Meq.MatrixMultiply(EE,proj)
  return Ej0;

### BEAM with projection -- fast
def EJones_P (ns,array,sources,radec0,meptable=None,solvables=[],solvable=False, name="E"):
  Bx={}
  By={}
  for station in array.stations():
   Bx[station] = makebeam(ns,station=station,meptable=meptable,solvable=solvable,solvables=solvables);
   By[station] = makebeam(ns,pol='Y',station=station,meptable=meptable,solvable=solvable,solvables=solvables);

  Ej0 = ns[name];

  # get array xyz
  xyz=array.xyz();

  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    radec=src.direction.radec()
    Ej = Ej0(dirname);

    for station in array.stations():
        # create Az,El per station, per source
        azelnode=ns.azel(dirname,station)<<Meq.AzEl(radec=src.direction.radec(),xyz=xyz(station))
        # projection
        az=ns.az(dirname,station)<<Meq.Selector(azelnode,multi=True,index=[0])
        el=ns.el(dirname,station)<<Meq.Selector(azelnode,multi=True,index=[1])
        # sin,cosines
        az_C=ns.az_C(dirname,station)<<Meq.Cos(az);
        az_S=ns.az_S(dirname,station)<<Meq.Sin(az);
        el_S=ns.el_S(dirname,station)<<Meq.Sin(el);
        proj=ns.proj(dirname,station)<<Meq.Matrix22(el_S*az_C,az_S,Meq.Negate(el_S*az_S),az_C);

        Xediag = ns.Xediag(dirname,station) << Meq.Compounder(children=[azelnode,Bx[station]],common_axes=[hiid('l'),hiid('m')])
        Yediag = ns.Yediag(dirname,station) << Meq.Compounder(children=[azelnode,By[station]],common_axes=[hiid('l'),hiid('m')])
        # create E matrix
        EE=ns.E0(dirname,station)<<Meq.Matrix22(Xediag,0,0,Yediag);
        Ej(station) <<Meq.MatrixMultiply(EE,proj)
  return Ej0;
