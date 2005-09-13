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
  Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,label=label): 
   by default, stokesI=1.0 and dec=pi/2 and all other node stubs are zero

  Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,ns=ns,label=label): 
   by default, stokesI=1.0 and dec=pi/2 and all other node stubs are zero,
   composed into one subtree as well.
 
 Other methods:
 compose(ns=ns) : composes the six subtrees into one subtree
 compose(ns=ns,label=label): composes with the sixpack root node having
    given label
 decompose() : decomposes the root into six subtrees
  in composed state, root !=None,
  in decomposed state, root ==None
 sixpack(ns=ns): if already composed, return the sixpack subtree,
  else, first compose it using given nodescope and return it
 iquv(ns=ns): compose the fourpack using the given nodescope 
  and return it
 radec(ns=ns): compose the twopack using the given nodescope and
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
      __sixpack: Root of the Sixpack subtree
      __iquv: root of fourpack subtree
      __radec: root of radec subtree
 """

 def __init__(self,**pp):
   """Possible input (and defalut values) for the constructor are:
      Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,label=label): roots of 
         the six subtrees but not composed
      Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,ns=ns): roots of
       the six subtrees, composed into one subtree
   """

   pp.setdefault('label',None)
   pp.setdefault('ns',None)
   pp.setdefault('type','Sixpack')
   pp.setdefault('ra',0)
   pp.setdefault('dec',math.pi/2)
   pp.setdefault('stokesI',1.0)
   pp.setdefault('stokesQ',0)
   pp.setdefault('stokesU',0)
   pp.setdefault('stokesV',0)
   TDL_common.Super.__init__(self, **pp)
   self.__label=pp['label']
   self.__sI=pp['stokesI']
   self.__sQ=pp['stokesQ']
   self.__sU=pp['stokesU']
   self.__sV=pp['stokesV']
   self.__RA=pp['ra']
   self.__Dec=pp['dec']
   # remember the given nodescope, if any
   self.__ns=pp['ns']
   # do not accept root of sixpack as constructor input
   self.__sixpack=None
   # root of 2pack and 4pack
   self.__radec=None
   self.__iquv=None

   # at least one subtree should be given as input to the constructor
   # try to compose
   my_ns=pp['ns']
   my_name=pp['label']
   print my_ns
   print my_name
   if  my_ns!=None and my_name !=None:
     # compose with given label
     self.__sixpack=my_ns.sixpack(q=my_name)<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)

 # common methods to get/set an item from the Sixpack, if input is None,
 # item is returned, else item is set to new value given as input.
 def ra(self,val=None):
  if val!=None:
   self.__RA=val
  return self.__RA

 def dec(self,val=None):
  if val!=None:
   self.__Dec=val
  return self.__Dec

 def stokesI(self,val=None):
  if val!=None:
   self.__sI=val
  return self.__sI

 def stokesQ(self,val=None):
  if val!=None:
   self.__sQ=val
  return self.__sQ

 def stokesU(self,val=None):
  if val!=None:
   self.__sU=val
  return self.__sU

 def stokesV(self,val=None):
  if val!=None:
   self.__sV=val
  return self.__sV
 
 def nodescope(self,val=None):
  if val!=None:
   self.__ns=val
  return self.__ns
 
 # decompose the sixpack into six node stubs
 def decompose(self):
  # get node stubs, make root=None
  if self.__sixpack!=None:
   child_list=self.__sixpack.children
   self.__RA=child_list[0][1]
   self.__Dec=child_list[1][1]
   self.__sI=child_list[2][1]
   self.__sQ=child_list[3][1]
   self.__sU=child_list[4][1]
   self.__sV=child_list[5][1]
   self.__sixpack=None
  else:
   _dprint(0,"Cannot decompose an empty subtree") 

 # compose the sixpack from the six node stubs
 def compose(self,ns=None):
  if self.__sixpack !=None:
   _dprint(1,"Warning: composing an already exsisting subtree")
  # try to compose
  my_ns=ns
  if my_ns!=None:
   #update nodescope
   self.__ns=ns
  else:
   #no nodescope given, use default nodescope
   my_ns=self.__ns
  my_name=self.__label
  if  my_ns!=None and my_name !=None:
    # compose with given label
     self.__sixpack=my_ns.sixpack(q=my_name)<<Meq.Composer(self.__RA,\
       self.__Dec,self.__sI,self.__sQ,self.__sU,self.__sV)
  else:
   _dprint(0,"Cannot compose when the  nodescope is None") 
  

 # return the sixpack from the six node stubs
 def sixpack(self,ns=None):
  if self.__sixpack==None:
   # first try to compose
   self.compose(nodescope,ns)
  return self.__sixpack


 # return the 4pack from the six node stubs
 def iquv(self,ns=None):
  my_ns=ns
  if my_ns!=None:
   #update nodescope
   self.__ns=ns
  else:
   #no nodescope given, use default nodescope
   my_ns=self.__ns
  my_name=self.__label
  if  my_ns!=None and my_name !=None:
    # compose with given label
    self.__iquv=my_ns.iquv(q=my_name)<<Meq.Composer(self.__sI,self.__sQ,self.__sU,self.__sV)
  else:
   _dprint(0,"Cannot compose iquv when the  nodescope is None") 
  # finally return
  return self.__iquv


 # return the 2pack from the six node stubs
 def radec(self,ns=None):
  my_ns=ns
  if my_ns!=None:
   #update nodescope
   self.__ns=ns
  else:
   #no nodescope given, use default nodescope
   my_ns=self.__ns
  my_name=self.__label
  if  my_ns!=None and my_name !=None:
    # compose with given label
    self.__radec=my_ns.radec(q=my_name)<<Meq.Composer(self.__RA,self.__Dec)
  else:
   _dprint(0,"Cannot compose radec when the nodescope is None") 
  return self.__radec



 # print a summary
 def oneliner(self):
  s=TDL_common.Super.oneliner(self)
  s+=":{ "
  s+=" sixpack= "+str(self.__sixpack)
  s+=" iquv= "+str(self.__iquv)
  s+=" radec= "+str(self.__radec)
  s+=" }"
  if self.__sixpack !=None:
   s+=" state 'composed'"
  else:
   s+=" state 'decomposed'"
  print s
  return s

 def display(self,txt=None,full=False):
  ss=TDL_common.Super.display(self,txt=txt,end=False)
  print "  StokesI (node stub)= "+str(self.__sI)
  print "  StokesQ (node stub)= "+str(self.__sQ)
  print "  StokesU (node stub)= "+str(self.__sU)
  print "  StokesV (node stub)= "+str(self.__sV)
  print "  RA      (node stub)= "+str(self.__RA)
  print "  Dec     (node stub)= "+str(self.__Dec)
  print "  sixpack (subtree)  = "+str(self.__sixpack)
  print "  iquv    (subtree)  = "+str(self.__iquv)
  print "  radec   (subtree)  = "+str(self.__radec)
  print "  nodescope (nodescope)="+str(self.__ns)
  if self.__sixpack !=None:
   print "  state is 'composed'"
  else:
   print "  state is 'decomposed'"
  TDL_common.Super.display_end(self,ss)

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
  my_sp=TDL_Sixpack.Sixpack(label='test',ns=ns,
    ra=radec['RA'],dec=radec['Dec'],stokesI=iquv['StokesI'],stokesQ=iquv['StokesQ'],\
    stokesU=iquv['StokesU'],stokesV=iquv['StokesV'])
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
    stokesU=my_sp.stokesU())

  my_sp1.display()

