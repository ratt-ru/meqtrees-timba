#!/usr/bin/env python

## Sixpack Object

from Timba.Meq import meq
from Timba.Trees import TDL_common
from Timba import utils
from Timba.TDL import *

_dbg = utils.verbosity(0, name='Sixpack')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf   

class Sixpack(TDL_common.Super):
 """
 Sixpack(root=root,label=label) : gives only the root of the sbutree
 Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,label=label): roots of 
  the six subtrees but not composed
 Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,nodescope=ns,label=label): 
     node stubs, of the six subtrees, composed into one subtree as root
 compose(nodescope=ns) : composes the six subtrees into one subtree
 compose(nodescope=ns,label=label): composes with the root node having
    given label
 decompose() : decomposes the root into six subtrees
  in composed state, root !=None,
  in decomposed state, root ==None
 setI(sI): replaces the I subtreee
 setQ(sQ): replaces the Q subtreee
 setU(sU): replaces the U subtreee
 setV(sV): replaces the V subtreee
 setRA(RA): replaces the RA subtreee
 setDec(Dec): replaces the Dec subtreee
  if sixpack is composed (root !=None), it is first decomposed
  before this is done
 getI(),getQ(),getU(),getV(),getRA(),getDec(),getRoot()
  returns the subtrees, or None

 Sixpack contains:
      __label: label of root node, if any

      node stubs
      __sI:
      __sQ:
      __sU:
      __sV:
      __RA:
      __Dec: six stubs for the six subtrees
      __root: Root of the Sixpack subtree
 """

 def __init__(self,**pp):
   """Possible input (and defalut values) for the constructor are:
      Sixpack(root=root) : gives only the root of the sbutree
      Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec): roots of the six subtrees
         but not composed
      Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,nodescope=ns): roots of
       the six subtrees, composed into one subtree as root
   """

   pp.setdefault('label',None)
   pp.setdefault('nodescope',None)
   pp.setdefault('type','Sixpack')
   pp.setdefault('RA',None)
   pp.setdefault('Dec',None)
   pp.setdefault('sI',None)
   pp.setdefault('sQ',None)
   pp.setdefault('sU',None)
   pp.setdefault('sV',None)
   pp.setdefault('root',None)
   TDL_common.Super.__init__(self, **pp)
   self.__label=pp['label']
   self.__root=pp['root']
   self.__sI=pp['sI']
   self.__sQ=pp['sQ']
   self.__sU=pp['sU']
   self.__sV=pp['sV']
   self.__RA=pp['RA']
   self.__Dec=pp['Dec']

   if  pp['RA'] !=None and pp['Dec']!=None and\
     pp['sI'] !=None and pp['sQ'] !=None and\
     pp['sU'] !=None and pp['sV'] !=None:
    # try to compose
    my_ns=pp['nodescope']
    my_name=pp['label']
    if  my_ns!=None and my_name !=None:
     # compose with given label
     self.__root=my_ns[my_name]<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
    elif my_ns !=None: # compose with defalut label
     self.__root=my_ns<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
   
 # traditional getter and setter methods
 # getter methods return the node stubs
 # setter methods should be followed by a compose() to create the 
 # subtree 
 def setI(self,I):
  self.__sI=I
 def getI(self):
  return self.__sI
 def setQ(self,Q):
  self.__sQ=Q
 def getQ(self):
  return self.__sQ
 def setU(self,U):
  self.__sU=U
 def getU(self):
  return self.__sU
 def setV(self,V):
  self.__sV=V
 def getV(self):
  return self.__sV
 def setRA(self,RA):
  self.__RA=RA
 def getRA(self):
  return self.__RA
 def setDec(self,Dec):
  self.__Dec=Dec 
 def getDec(self):
  return self.__Dec
 def setRoot(self,root):
  self.__root=root
  # set all node stubs to None
  self.__sI=None
  self.__sQ=None
  self.__sU=None
  self.__sV=None
  self.__RA=None
  self.__Dec=None
 def getRoot(self):
  return self.__root

 def decompose(self):
  # get node stubs, make root=None
  if self.__root !=None:
   child_list=self.__root.children
   self.__RA=child_list[0][1]
   self.__Dec=child_list[1][1]
   self.__sI=child_list[2][1]
   self.__sQ=child_list[3][1]
   self.__sU=child_list[4][1]
   self.__sV=child_list[5][1]
   self.__root=None
  else:
   _dprint(0,"Cannot decompose an empty subtree") 

 def compose(self,nodescope,label=None):
  if self.__root !=None:
   _dprint(1,"Warning: composing an already exsisting subtree")
  # try to compose
  my_ns=nodescope
  if label==None:
   my_name=self.__label
  else:
   my_name=label
  if self.__sI!=None and self.__sQ!=None and\
    self.__sU!=None and self.__sV !=None and\
    self.__RA!=None and self.__Dec !=None:
   if  my_ns!=None and my_name !=None:
    # compose with given label
     self.__root=my_ns[my_name]<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
   elif my_ns !=None: # compose with defalut label
     self.__root=my_ns<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
  else:
   _dprint(0,"Cannot compose when the (IQUV)(RA,Dec) node stubs are empty") 
  
 # 
 def oneliner(self):
  s=TDL_common.Super.oneliner(self)
  s+="type '"+self.type()+"' label '"+self.label()+"'"
  if self.__root !=None:
   s+=" state 'composed'"
  else:
   s+=" state 'decomposed'"
  return s

 def display(self,txt=None,full=False):
  s=TDL_common.Super.display(self,txt=txt,end=False)
  print s
  print str(self) 
  TDL_common.Super.display_end(self)

 # Print
 def __str__(self):
   temp_str="Sixpack: {I="+str(self.getI())
   temp_str+=",Q="+str(self.getQ())
   temp_str+=",U="+str(self.getU())
   temp_str+=",V="+str(self.getV())
   temp_str+=",RA="+str(self.getRA())
   temp_str+=",Dec="+str(self.getDec())
   temp_str+=",Root="+str(self.getRoot())
   temp_str+="}"
   return temp_str



################################################################
if __name__=='__main__':
  ns=NodeScope()
  from Timba.Contrib.JEN import MG_JEN_sixpack
  from Timba.Trees import TDL_Sixpack 
  my_name='foo'
  sixpack_stubs=MG_JEN_sixpack.newstar_source(ns, name=my_name,I0=10, SI=[0.1],f0=1e6,RA=0.0, Dec=0.0,trace=0)
  iquv=sixpack_stubs['iquv']
  radec=sixpack_stubs['radec']
  my_sp=TDL_Sixpack.Sixpack(label='test',nodescope=ns,
    RA=radec['RA'],Dec=radec['Dec'],sI=iquv['StokesI'],sQ=iquv['StokesQ'],\
    sU=iquv['StokesU'],sV=iquv['StokesV'])
  my_sp.display()
  # decompose to get back the node stubs
  my_sp.decompose()
  my_sp.display()
  # this should give an error
  my_sp.decompose()
  # create a new nodescope
  ns1=NodeScope('1')
  # compose node stubs in the new nodescope
  my_sp.compose(ns1)
  my_sp.display()
  # resolve both node scopes
  ns.Resolve()
  ns1.Resolve()
