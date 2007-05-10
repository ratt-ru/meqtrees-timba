from Timba.TDL import *
from Meow.Utils import *
from Meow.Direction import *
from Meow.PointSource import *
from Meow.GaussianSource import *
#from Meow.Shapelet import *

from Timba.LSM.LSM import LSM


def point_and_extended_sources (ns,lsm,tablename='',count=100):
  """ define two extended sources: positions and flux densities """
  parm_options = record(
      use_previous=False,
      table_name=tablename,
      node_groups='Parm');
  

  source_model = []

##
## Note: conversion from AIPS++ componentlist Gaussians to Gussian Nodes
### eX, eY : multiply by 2
### eP: change sign

  plist=lsm.queryLSM(count=count)

  for pu in plist:
     (ra,dec,sI,sQ,sU,sV,SIn,f0,RM)=pu.getEssentialParms(ns)
     (eX,eY,eP)=pu.getExtParms()
     # scale 2 difference
     eX=eX*2
     eY=eY*2
     eP=-eP
     if eX!=0 or eY!=0 or eP!=0:
         # Gaussians
         source_model.append( GaussianSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP));
     else:
         # point Sources
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  direction=Direction(ns,pu.name,ra,dec),
                  spi=SIn,freq0=f0, RM=RM));



  return source_model
