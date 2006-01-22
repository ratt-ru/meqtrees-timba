#!/usr/bin/env python

## Sixpack Object

from Timba.Meq import meq
from Timba.Trees import TDL_common
from Timba.Trees import TDL_Parmset  
from Timba import utils
from Timba.TDL import *
import math

_dbg = utils.verbosity(0, name='Sixpack')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf   

class Sixpack_Point(TDL_common.Super):
 """
 Constructors:
  Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,label=label): 
   by default, stokesI=1.0 and dec=pi/2 and all other node stubs are zero

  Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,ns=ns,label=label): 
   by default, stokesI=1.0 and dec=pi/2 and all other node stubs are zero,
   composed into one subtree as well.
 
 Other methods:
 decompose() : decomposes the root into six subtrees
  in composed state, sixpack !=None,
  in decomposed state, sixpack ==None
 sixpack(ns=ns): if already composed, return the sixpack subtree,
  else, first compose it using given nodescope and return it
 iquv(ns=ns): compose the fourpack using the given nodescope 
  and return it or return an already composed subtree
 radec(ns=ns): compose the twopack using the given nodescope and
  return it or return an already composed subtree

 stokesI(new_stokesI):
  if called without any input, returns the StokesI,
  else, set StokesI node stub to the new value
 stokesQ(new_stokesQ):
 stokesU(new_stokesQ):
 stokesV(new_stokesQ): same as above stokesI()

 ra(new_RA): 
 dec(new_Dec): same as above stokesI()

 

 Sixpack_Point contains:
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
   # pp.setdefault('type','Sixpack')
   pp.setdefault('ra',0)
   pp.setdefault('dec',math.pi/2)
   pp.setdefault('stokesI',1.0)
   pp.setdefault('stokesQ',0)
   pp.setdefault('stokesU',0)
   pp.setdefault('stokesV',0)


   TDL_common.Super.__init__(self, type='Sixpack_point', **pp)
   # TDL_common.Super.__init__(self, **pp)


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


   # 2 types of 2x2 cohaerency matrices
   self.__coh22_linear = None
   self.__coh22_circular = None

   # at least one subtree should be given as input to the constructor
   # try to compose
   my_ns=pp['ns']
   my_name=pp['label']
   #print my_ns
   #print my_name
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
   self.__iquv=None
   self.__radec=None
  else:
   _dprint(0,"Cannot decompose an empty subtree") 

 # compose the sixpack from the six node stubs
 def sixpack(self,ns=None):
  if self.__sixpack !=None:
   return self.__sixpack
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

  return self.__sixpack

 # return the 4pack from the six node stubs
 def iquv(self,ns=None):
  if self.__iquv!=None:
   return self.__iquv
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
  if self.__radec!=None:
   return self.__radec
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
  indent1=2*' '
  # ss.append(" ")
  ss.append(indent1+"- stokesI (node stub)= "+str(self.__sI))
  ss.append(indent1+"- stokesQ (node stub)= "+str(self.__sQ))
  ss.append(indent1+"- stokesU (node stub)= "+str(self.__sU))
  ss.append(indent1+"- stokesV (node stub)= "+str(self.__sV))
  ss.append(indent1+"- ra      (node stub)= "+str(self.__RA))
  ss.append(indent1+"- dec     (node stub)= "+str(self.__Dec))
  ss.append(indent1+"- sixpack (subtree)  = "+str(self.__sixpack))
  ss.append(indent1+"- iquv    (subtree)  = "+str(self.__iquv))
  ss.append(indent1+"- radec   (subtree)  = "+str(self.__radec))
  ss.append(indent1+"- linear  (subtree)  = "+str(self.__coh22_linear))
  ss.append(indent1+"- circular(subtree)  = "+str(self.__coh22_circular))
  ss.append(indent1+"- ns      (nodescope)= "+str(self.__ns))
  if self.__sixpack !=None:
   ss.append(indent1+"- State is 'composed'")
  else:
   ss.append(indent1+"- State is 'decomposed'")
  # ss.append(" ")
  return TDL_common.Super.display_end(self,ss)

 # generic string
 def __str__(self):
  return self.oneliner()

#----------------------------------------------------------------------
# Function dealing with conversion to a 2x2 cohaerency matrix
# JEN, 10 oct 2005

 def coh22(self, ns, polrep='linear', name='nominal'):
     """Make a 2x2 nominal cohaerency matrix of the specified polarisation representation"""
     if polrep=='circular':
         if not self.__coh22_circular:
             self.__coh22_circular = Sixpack2circular (ns, self, name=name)
         return self.__coh22_circular
     else:
         if not self.__coh22_linear:
             self.__coh22_linear = Sixpack2linear (ns, self, name=name)
         return self.__coh22_linear

 def clone(self,**pp):
     """workaround to recreate a saved Sixpack object by using the 7 node
        stubs, I,Q,U,V,Ra,Dec and the __sixpack. First we use 
        the default constructor and call this method. We need this because
        we do not have a constructor that can give the sixpack root.
     """
     pp.setdefault('sixpack',None)
     pp.setdefault('ns',None)
     # replace the root node stubs
     self.__sixpack=pp['sixpack']
     self.__ns=pp['ns']
     return self

################################################################
class Sixpack_Patch(TDL_common.Super):
 """
 Constructors:
  Sixpack(root=root,label=label): 
   the above two are mandetory, only in a patch the 'root' input argument
   should be given. Note that by default both are set to None. 
 
 Other methods:
 root() : return the root 

 Sixpack_Patch contains:
      __label: label of root node, if any
      __root: root of subtree
 """

 def __init__(self,**pp):
   """Possible input (and defalut values) for the constructor are:
      Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,label=label): roots of 
         the six subtrees but not composed
      Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,ns=ns): roots of
       the six subtrees, composed into one subtree
   """

   pp.setdefault('label',None)
   pp.setdefault('root',None)
   pp.setdefault('type','Sixpack')
   TDL_common.Super.__init__(self, **pp)
   self.__label=pp['label']
   self.__root=pp['root']

 def root(self):
  return self.__root

 # print a summary
 def oneliner(self):
  s=TDL_common.Super.oneliner(self)
  s+=":{ "
  s+=" root= "+str(self.__root)
  s+=" }"
  print s
  return s

 def display(self,txt=None,full=False):
  ss=TDL_common.Super.display(self,txt=txt,end=False)
  indent1=2*' '
  ss.append(indent1+"- root (node stub)= "+str(self.__root))
  return TDL_common.Super.display_end(self,ss)

 # generic string
 def __str__(self):
  return self.oneliner()


#----------------------------------------------------------------------
# Function dealing with conversion to a 2x2 cohaerency matrix
# JEN, 10 oct 2005
# NB: For a patch, this function requires a little thought (ubvricks etc)....
#     Requires more children (size of uv-plane etc)

 def coh22(self, ns, polrep='linear', name='nominal'):
     """Make a 2x2 nominal cohaerency matrix of the specified polarisation representation"""
     return 'not supported yet'

 def clone(self,**pp):
     """workaround to recreate a saved Sixpack object by using the 7 node
        stubs, I,Q,U,V,Ra,Dec and the __sixpack. We need this because
        we do not have a constructor that can give all of these.
        This does nothing because this is a patch
     """
     return self
 

#######################################################################
class Sixpack:
 """
 Constructors:
  Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,label=label): 
   by default, stokesI=1.0 and dec=pi/2 and all other node stubs are zero

  Sixpack(stokesI=sI,stokesQ=sQ,stokesU=sU,stokesV=sV,ra=RA,dec=Dec,ns=ns,label=label): 
   by default, stokesI=1.0 and dec=pi/2 and all other node stubs are zero,
   composed into one subtree as well.
 
 Other methods:
 decompose() : decomposes the root into six subtrees
  in composed state, sixpack !=None,
  in decomposed state, sixpack ==None
 sixpack(ns=ns): if already composed, return the sixpack subtree,
  else, first compose it using given nodescope and return it
 iquv(ns=ns): compose the fourpack using the given nodescope 
  and return it or return an already composed subtree
 radec(ns=ns): compose the twopack using the given nodescope and
  return it or return an already composed subtree

 stokesI(new_stokesI):
  if called without any input, returns the StokesI,
  else, set StokesI node stub to the new value
 stokesQ(new_stokesQ):
 stokesU(new_stokesQ):
 stokesV(new_stokesQ): same as above stokesI()

 ra(new_RA): 
 dec(new_Dec): same as above stokesI()

 

 Sixpack_Point contains:
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
 """
 Constructors:
  Sixpack(root=root,label=label): 
   the above two are mandetory, only in a patch the 'root' input argument
   should be given. Note that by default both are set to None. 
 
 Other methods:
 root() : return the root 

 Sixpack_Patch contains:
      __label: label of root node, if any
      __root: root of subtree
 """
 def __init__(self,**pp):
   """
    Depending on the input, this can be a Sixpack_Point or Sixpack_Patch
   """
   pp.setdefault('root',None)
   if pp['root']!=None: # create a Sixpack_Patch
    #print "Create Patch"
    self.__obj=Sixpack_Patch(**pp)
    self.__point=False
   else:
    #print "Create Point"
    self.__obj=Sixpack_Point(**pp)
    self.__point=True
  
   # Define its Parmset object
   self.Parmset = TDL_Parmset.Parmset(**pp)
   self.Parmset.quals(dict(q=self.label()))       # punit...?
   # print dir(self)






 def ra(self,val=None):
  if self.__point:
   return self.__obj.ra(val)
  else:
   return None

 def dec(self,val=None):
  if self.__point:
   return self.__obj.dec(val)
  else:
   return None

 def stokesI(self,val=None):
  if self.__point:
   return self.__obj.stokesI(val)
  else:
   return None

 def stokesQ(self,val=None):
  if self.__point:
   return self.__obj.stokesQ(val)
  else:
   return None

 def stokesU(self,val=None):
  if self.__point:
   return self.__obj.stokesU(val)
  else:
   return None

 def stokesV(self,val=None):
  if self.__point:
   return self.__obj.stokesV(val)
  else:
   return None

 def nodescope(self,val=None):
  if self.__point:
   return self.__obj.nodescope(val)
  else:
   return None

 # decompose the sixpack into six node stubs
 def decompose(self):
  if self.__point:
   self.__obj.decompose()
  else:
   return 

 # compose the sixpack from the six node stubs
 def sixpack(self,ns=None):
  if self.__point:
   return self.__obj.sixpack(ns)
  else:
   return None

 # return the 4pack from the six node stubs
 def iquv(self,ns=None):
  if self.__point:
   return self.__obj.iquv(ns)
  else:
   return None

 # return the 2pack from the six node stubs
 def radec(self,ns=None):
  if self.__point:
   return self.__obj.radec(ns)
  else:
   return None


 # print a summary
 def oneliner(self):
  return self.__obj.oneliner()

 def display(self,txt=None,full=False):
  ss = self.__obj.display(txt,full)
  indent1=2*' '
  ss.append(indent1+' - '+str(self.Parmset.oneliner()))
  return ss

 # generic string
 def __str__(self):
  return self.oneliner()

 # the following method is only valid for a patch
 def root(self):
  if not self.__point:
   return self.__obj.root()
  else:
   return None

 # the following method is only valid for a patch
 def label(self,*nkw,**kw):
  return self.__obj.label(*nkw,**kw)

 def type(self,*nkw,**kw): 
  return self.__obj.type(*nkw,**kw)

 # the following method is used to see if this object is a patch or a point source
 def ispoint(self):
     return self.__point

 def clone(self,**kw):
   self.__obj.clone(**kw)
   return self

#----------------------------------------------------------------------
# Function dealing with conversion to a 2x2 cohaerency matrix
# JEN, 10 oct 2005

 def coh22(self, ns, polrep='linear', name='nominal'):
     """Make a 2x2 nominal cohaerency matrix of the specified polarisation representation"""
     return self.__obj.coh22(ns, polrep=polrep, name=name)


#######################################################################
# Convert an (LSM) Sixpack into visibilities for linearly polarised receptors:
  
def Sixpack2linear (ns, Sixpack, name='nominal'):
    """Make a 2x2 coherency matrix (coh22) by multiplication with the Stokes matrix"""
    punit = Sixpack.label()
    name = name+'_XYYX'
    coh22 = ns[name](q=punit) << Meq.Matrix22(
        (ns['XX'](q=punit) << Sixpack.stokesI() + Sixpack.stokesQ()),
        (ns['XY'](q=punit) << Meq.ToComplex( Sixpack.stokesU(), Sixpack.stokesV())),
        (ns['YX'](q=punit) << Meq.Conj( ns['XY'](q=punit) )),
        (ns['YY'](q=punit) << Sixpack.stokesI() - Sixpack.stokesQ())
        ) * 0.5
    return coh22

#--------------------------------------------------------------------------------------
# Convert an (LSM) Sixpack into visibilities for circularly polarised receptors:

def Sixpack2circular (ns, Sixpack, name='nominal'):
    """Make a 2x2 coherency matrix (coh22) by multiplication with the Stokes matrix"""
    punit = Sixpack.label()
    name = name+'_RLLR'
    coh22 = ns[name](q=punit) << Meq.Matrix22(
        (ns['RR'](q=punit) << Sixpack.stokesI() + Sixpack.stokesV()),
        (ns['RL'](q=punit) << Meq.ToComplex( Sixpack.stokesQ(), Sixpack.stokesU())),
        (ns['LR'](q=punit) << Meq.Conj( ns['RL'](q=punit) )),
        (ns['LL'](q=punit) << Sixpack.stokesI() - Sixpack.stokesV())
        ) * 0.5
    return coh22



#######################################################################
if __name__=='__main__':
  ns=NodeScope()
  from Timba.Trees import TDL_Sixpack 
  my_name='my_sixpack'
  # create some node stubs for the sixpack
  # first some parameters
  ns.f<<Meq.Parm(meq.polclog([1,0.1,0.01]))
  ns.t<<Meq.Parm(meq.polclog([0.01,0.1,1]))
  # next the node stubs
  stubI=ns['Istub']<<1.1*Meq.Sin(ns.f+ns.t)
  stubQ=ns['Qstub']<<2.0*Meq.Cos(ns.f)
  stubU=ns['Ustub']<<2.1*Meq.Sin(ns.f-2)
  stubV=ns['Vstub']<<2.1*Meq.Cos(ns.f-2)
  stubRA=ns['RAstub']<<2.1*Meq.Cos(ns.f-2)*Meq.Sin(ns.t)
  stubDec=ns['Decstub']<<2.1*Meq.Cos(ns.f-2)*Meq.Sin(ns.t)

  # now create the sixpack
  my_sp=TDL_Sixpack.Sixpack(label=my_name,\
   ns=ns, ra=stubRA,dec=stubDec,stokesI=stubI,\
   stokesQ=stubQ,stokesU=stubU,stokesV=stubV)
  my_sp.display()

  # Conversion to 2x2  cohaerency matrix
  print my_sp.coh22(ns)
  print my_sp.coh22(ns)
  print my_sp.coh22(ns, 'circular')
  print
  
  my_name='patch0'
  stubR=ns[my_name]<<1.1*Meq.Sin(ns.f+ns.t)+2.0*Meq.Cos(ns.f)-2.1*Meq.Sin(ns.f-2)
 
  my_sp_patch=TDL_Sixpack.Sixpack(label=my_name,root=stubR)

  # resolve the forest
  ns.Resolve()
  print "========================= Point "
  print dir(my_sp)
  my_sp.display()
  my_sp.decompose()
  print my_sp.stokesI()
  print my_sp.stokesQ()
  print my_sp.stokesU()
  print my_sp.stokesV()
  print my_sp.root()
  print my_sp.type()
  print "========================= Patch"
  print dir(my_sp_patch)
  my_sp_patch.display()
  my_sp_patch.decompose()
  print my_sp_patch.stokesI()
  print my_sp_patch.stokesQ()
  print my_sp_patch.stokesU()
  print my_sp_patch.stokesV()
  print my_sp_patch.root()

