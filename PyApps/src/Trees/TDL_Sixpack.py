#!/usr/bin/env python

## Sixpack Object

from Timba.Meq import meq
from Timba.Trees import TDL_common
from Timba import utils
from Timba.TDL import *
import math

_dbg = utils.verbosity(0, name='Sixpack')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf   

class Sixpack(TDL_common.Super):
 """
 Constructors:
  Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,label=label): 
   needs at least one node stub for the six subtrees but is not composed

  Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,nodescope=ns,label=label): 
   needs at least one node stubs for the six subtrees, 
   composed into one subtree as well.
 
 Other methods:
 compose(nodescope=ns) : composes the six subtrees into one subtree
 compose(nodescope=ns,label=label): composes with the sixpack root node having
    given label
 decompose() : decomposes the root into six subtrees
  in composed state, root !=None,
  in decomposed state, root ==None
 sixpack(nodescope=ns): if already composed, return the sixpack subtree,
  else, first compose it using given nodescope and return it
 iquv(nodescope=ns): compose the fourpack using the given nodescope 
  and return it
 radec(nodescope=ns): compose the twopack using the given nodescope and
  return it

 stokesI(new_stokesI):
  if called without any input, returns the StokesI,
  else, set StokesI node stub to the new value
 stokesQ(new_stokesQ):
 stokesU(new_stokesQ):
 stokesV(new_stokesQ): same as above stokesI()

 ra(new_RA): 
 dec(new_Dec): same as above stokesI()

 

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
      __iquv: root of fourpack subtree
      __radec: root of radec subtree
 """

 def __init__(self,**pp):
   """Possible input (and defalut values) for the constructor are:
      Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,label=label): roots of 
         the six subtrees but not composed
      Sixpack(sI=sI,sQ=sQ,sU=sU,sV=sV,RA=RA,Dec=Dec,nodescope=ns): roots of
       the six subtrees, composed into one subtree
   """

   pp.setdefault('label',None)
   pp.setdefault('nodescope',None)
   pp.setdefault('type','Sixpack')
   pp.setdefault('RA',0)
   pp.setdefault('Dec',math.pi/2)
   pp.setdefault('sI',0)
   pp.setdefault('sQ',0)
   pp.setdefault('sU',0)
   pp.setdefault('sV',0)
   TDL_common.Super.__init__(self, **pp)
   self.__label=pp['label']
   self.__sI=pp['sI']
   self.__sQ=pp['sQ']
   self.__sU=pp['sU']
   self.__sV=pp['sV']
   self.__RA=pp['RA']
   self.__Dec=pp['Dec']
   # remember the given nodescope, if any
   #self.__ns=pp['nodescope']
   # do not accept root of sixpack as constructor input
   self.__root=None
   # root of 2pack and 4pack
   self.__radec=None
   self.__iquv=None

   # at least one subtree should be given as input to the constructor
   if  pp['RA'] !=0 or pp['Dec']!=math.pi/2 or\
     pp['sI'] !=0 or pp['sQ'] !=0 or\
     pp['sU'] !=0 or pp['sV'] !=0:
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
   else: 
    _dprint(1,"Warning: at least one subtree should be given to the constructor") 


 # common methods to get/set an item from the Sixpack, if input is None,
 # item is returned, else item is set to new value given as input.
 def ra(self,val=None):
  if val==None:
   return self.__RA
  else:
   self.__RA=val

 def dec(self,val=None):
  if val==None:
   return self.__Dec
  else:
   self.__Dec=val

 def stokesI(self,val=None):
  if val==None:
   return self.__sI
  else:
   self.__sI=val

 def stokesQ(self,val=None):
  if val==None:
   return self.__sQ
  else:
   self.__sQ=val

 def stokesU(self,val=None):
  if val==None:
   return self.__sU
  else:
   self.__sU=val

 def stokesV(self,val=None):
  if val==None:
   return self.__sV
  else:
   self.__sV=val

 # decompose the sixpack into six node stubs
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

 # compose the sixpack from the six node stubs
 def compose(self,nodescope,label=None):
  if self.__root !=None:
   _dprint(1,"Warning: composing an already exsisting subtree")
  # try to compose
  my_ns=nodescope
  if label==None:
   my_name="sixpack(q="+self.__label+")"
  else:
   my_name="sixpack(q="+label+")"
  if self.__sI!=0 or self.__sQ!=0 or\
    self.__sU!=0 or self.__sV !=0 or\
    self.__RA!=0 or self.__Dec !=math.pi/2:
   if  my_ns!=None and my_name !=None:
    # compose with given label
     self.__root=my_ns[my_name]<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
   elif my_ns !=None: # compose with defalut label
     self.__root=my_ns<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
  else:
   _dprint(0,"Cannot compose when the (IQUV)(RA,Dec) node stubs are empty") 
  
 # return the sixpack from the six node stubs
 def sixpack(self,nodescope=None):
  if self.__root==None:
   #first try to compose
   self.compose(nodescope)
  return self.__root

 # return the 4pack from the six node stubs
 def iquv(self,nodescope=None,label=None):
  my_ns=nodescope
  if label==None:
   my_name="iquv(q="+self.__label+")"
  else:
   my_name="iquv(q="+label+")"
  if self.__sI!=0 or self.__sQ!=0 or\
    self.__sU!=0 or self.__sV !=0:
   if  my_ns!=None and my_name !=None:
    # compose with given label
     self.__iquv=my_ns[my_name]<<Meq.Composer(self.__sI,self.__sQ,self.__sU,self.__sV)
   elif my_ns !=None: # compose with defalut label
     self.__iquv=my_ns<<Meq.Composer(self.__sI,self.__sQ,self.__sU,self.__sV)
  else:
   _dprint(0,"Cannot compose iquv when the (IQUV) node stubs are empty") 
  # finally return
  return self.__iquv

 # return the 2pack from the six node stubs
 def radec(self,nodescope=None,label=None):
  my_ns=nodescope
  if label==None:
   my_name="radec(q="+self.__label+")"
  else:
   my_name="radec(q="+label+")"
  if self.__RA!=0 or self.__Dec!=math.pi/2:
   if  my_ns!=None and my_name !=None:
    # compose with given label
     self.__radec=my_ns[my_name]<<Meq.Composer(self.__RA,self.__Dec)
   elif my_ns !=None: # compose with defalut label
     self.__radec=my_ns<<Meq.Composer(self.__RA,self.__Dec)
  else:
   _dprint(0,"Cannot compose radec when the (RA,Dec) node stubs are empty") 
 
  return self.__radec

 # print a summary
 def oneliner(self):
  s=TDL_common.Super.oneliner(self)
  s+=" : {I="+str(self.__sI)
  s+=",Q="+str(self.__sQ)
  s+=",U="+str(self.__sU)
  s+=",V="+str(self.__sV)
  s+=",RA="+str(self.__RA)
  s+=",Dec="+str(self.__Dec)
  s+=",sixpack="+str(self.__root)
  s+=",iquv="+str(self.__iquv)
  s+=",radec="+str(self.__radec)
  s+="}"
  if self.__root !=None:
   s+=" state 'composed'"
  else:
   s+=" state 'decomposed'"
  return s

 def display(self,txt=None,full=False):
  ss=TDL_common.Super.display(self,txt=txt,end=False)
  TDL_common.Super.display_end(self,ss)
  return ss

 # generic string
 def __str__(self):
  return self.oneliner()


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

  # try to get some subtrees
  iquv_tree=my_sp.iquv()
  print iquv_tree
  iquv_tree=my_sp.iquv(ns)
  print iquv_tree
  my_sp.display()

  radec=my_sp.radec(ns1)
  my_sp.display()
  my_sp1=TDL_Sixpack.Sixpack(label='test1',\
    sU=my_sp.stokesU())

  my_sp1.display()

