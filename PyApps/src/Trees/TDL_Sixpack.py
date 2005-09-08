#!/usr/bin/env python

## Sixpack Object

from Timba.LSM.LSM import *
#from Timba.TDL import Settings
#from Timba.LSM.LSM_GUI import *
from Timba.Meq import meq
from Timba.Trees import TDL_common

from Timba import utils
from Timba.TDL import *

_dbg = utils.verbosity(0, name='Sixpack')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf   

class Sixpack(TDL_common.Super):
 """Sixpack contains:
      __name: unique name to find the root of subtree

      __ns: NodeScope object, to find the forest
      __mqs: MeqServer Proxy object to send requests
      __cells: Cells of the current request
      __lsm: LSM using this Sixpack
        this is needed to access the global meqserver proxy
        and to get current time,freq values
        If mqs==None, we can use the mqs of the lsm
        also if cell==None, we can use the cell of the lsm

      __sI:
      __sQ:
      __sU:
      __sV:
      __RA:
      __Dec: six vellsets of the current response
      __root: Root of the Sixpack subtree

      __type: type of object
 """ 

 # class attributes for representation
 __color=['R','G','B']

 # input for constructor: 
 def __init__(self,**pp):
   """Possible input (and defalut values) for the constructor are:
      name: unique name for the root of the subtree, 
           generally the name of the PUnit (None)
      ns: NodeScope object (None)
      # Node Stubs
      RA: Right Ascention (0)
      Dec: Declination (0)
      StokesI: Stokes I
      StokesQ: Stokes Q
      StokesU: Stokes U
      StokesV: Stokes V
      """

   pp.setdefault('name',None)
   pp.setdefault('label',None)
   pp.setdefault('ns',None)
   pp.setdefault('type','Sixpack')
   pp.setdefault('RA',0)
   pp.setdefault('Dec',0)
   pp.setdefault('StokesI',0)
   pp.setdefault('StokesQ',0)
   pp.setdefault('StokesU',0)
   pp.setdefault('StokesV',0)
   TDL_common.Super.__init__(self, **pp)
   self.__name=pp['name']
   self.__label=pp['label']

   #remember the nodescope
   self.__ns=pp['ns']
   # create trees using JEN code, if there is a node scope
   if self.__ns !=None:
    self.__iquv={'StokesI':pp['StokesI'],'StokesQ':pp['StokesQ'],\
                 'StokesU':pp['StokesU'],'StokesV':pp['StokesV']}
    self.__radec={'RA':pp['RA'], 'Dec':pp['Dec']}
    # check whether we already have a node with given name
    if self.__ns[self.__name].initialized() !=True:
     self.__root=self.__ns[self.__name]<<Meq.Composer(self.__radec['RA'],self.__radec['Dec'],self.__iquv['StokesI'],self.__iquv['StokesQ'],self.__iquv['StokesU'],self.__iquv['StokesV'])
    else: # if this node has already being defined
     _dprint(0,"Node already defined")
     self.__root=None
     #raise exception
     raise Timba.TDL.TDLimpl.NodeRedefinedError

   else:
    self.__root=None
    self.__iquv=None
    self.__radec=None
   
   # set everything else to None
   self.__sI=None
   self.__sQ=None
   self.__sU=None
   self.__sV=None
   self.__RA=None
   self.__Dec=None
   self.__lsm=None
   self.__cells=None

 # traditional getter and setter methods
 # setter methods need the vellset as input
 # setter methods are private
 # getter methods return the value array
 def __setI(self,I):
  self.__sI=I
 def getI(self):
  if self.__sI==None:
   return 0
  return self.__sI.value
 def __setQ(self,Q):
  self.__sQ=Q
 def getQ(self):
  if self.__sQ==None:
   return 0
  return self.__sQ.value
 def __setU(self,U):
  self.__sU=U
 def getU(self):
  if self.__sU==None:
   return 0
  return self.__sU.value
 def __setV(self,V):
  self.__sV=V
 def getV(self):
  if self.__sU==None:
   return 0
  return self.__sV.value
 def __setRA(self,RA):
  self.__RA=RA
 def getRA(self):
  if self.__RA==None:
   return 0
  return self.__RA.value[0]
 def __setDec(self,Dec):
  self.__Dec=Dec 
 def getDec(self):
  if self.__Dec==None:
   return 0
  return self.__Dec.value[0]
 # Cells
 def setCells(self,cl):
  self.__cells=cl
 def getCells(self):
  return self.__cells
 # MeqServer Proxy
 def setMQS(self,cl):
  self.__mqs=cl
 def getMQS(self):
  return self.__mqs
 # NodeScope
 def setNS(self,cl):
  self.__ns=cl
 def getNS(self):
  return self.__ns
 # setting the meqtree root
 def setRoot(self,root):
  self.__root=root
 # link back to the LSM
 def setLSM(self,lsm):
  self.__lsm=lsm
 def label(self):
  return self.__name

 # create the trees
 def createTree(self,**kw): 
  if kw.has_key('name'):
   self.__name=kw['name']
  if self.__ns!=None and self.__name !=None:
   if kw.has_key['RA']:
    RA=kw['RA']
   else:
    RA=0
   if kw.has_key['Dec']:
    Dec=kw['Dec']
   else:
    Dec=0
   if kw.has_key['StokesI']:
    sI=kw['StokesI']
   else:
    sI=0
   if kw.has_key['StokesQ']:
    sQ=kw['StokesQ']
   else:
    sQ=0
   if kw.has_key['StokesU']:
    sU=kw['StokesU']
   else:
    sU=0
   if kw.has_key['StokesV']:
    sV=kw['StokesV']
   else:
    sV=0

   self.__iquv={'StokesI':kw['sI'],'StokesQ':kw['sQ'],\
                 'StokesU':kw['sU'],'StokesV':kw['sV']}
   self.__radec={'RA':kw['RA'], 'Dec':kw['Dec']}
   if self.__ns[self.__name].initialized() !=True:
     self.__root=self.__ns[self.__name]<<Meq.Composer(self.__radec['RA'],self.__radec['Dec'],self.__iquv['StokesI'],self.__iquv['StokesQ'],self.__iquv['StokesU'],self.__iquv['StokesV'])
   else: # if this node has already being defined
     _dprint(0,"Node already defined")
     self.__root=None

 def updateVells(self,name=None):
  """ update Vells according to the new cells, 
      the name of the Sixpack can be given as 'name' """
  if (self.__lsm!=None) and (self.__lsm.cells!=None) and\
   (self.__lsm.mqs!=None):
   my_cells=self.__lsm.cells
   my_mqs=self.__lsm.mqs
  elif self.__cells!=None and self.__mqs!=None:
   my_cells=self.__cells
   my_mqs=self.__mqs
  else:
   _dprint(0,"Cannot update Vells please setup your meqserver proxy before you do this")
   return

  # create request object
  my_request = meq.request(cells=my_cells, eval_mode=0)
  if self.__name ==None:
   my_name=name
  else:
   my_name=self.__name
  # if name is still None, get name from root
  if my_name==None and self.__ns!=None:
   my_name=self.__root.name
  my_args=meq.record(name=my_name, request=my_request)
  my_result=my_mqs.meq('Node.execute', my_args,wait=True)
  # update Vells 
  self.__setRA(my_result.result.vellsets[0])
  self.__setDec(my_result.result.vellsets[1])
  self.__setI(my_result.result.vellsets[2])
  self.__setQ(my_result.result.vellsets[3])
  self.__setU(my_result.result.vellsets[4])
  self.__setV(my_result.result.vellsets[5])


 # returns the size of the values corresponding to the given (t,f) pair
 # and the quantity 'A','I','Q','U','V','RA','Dec'
 # returns [l,m] for lxm array size
 def getVellsDimension(self,type,freq_index,time_index):
  if (self.__lsm!=None) and (self.__lsm.cells!=None):
   my_cells=self.__lsm.cells
  elif self.__cells!=None:
   my_cells=self.__cells
  else:
   _dprint(0,"Cannot get Vells please setup your meqserver proxy before you do this")
   return None


  # range error check
  if (my_cells.segments.freq.start_index > freq_index) or\
    (my_cells.segments.freq.end_index < freq_index):
    _dprint(0,"Index error, Frequency %d",freq_index)
    freq_index=my_cells.segments.freq.start_index
  if (my_cells.segments.time.start_index > time_index) or\
    (my_cells.segments.time.end_index < time_index):
    _dprint(0,"Index error, Time %d",time_index)
    time_index=my_cells.segments.time.start_index
  if type=='A' or type=='I':
   # expect a vellset
   try:
    shape=self.__sI.shape
    if len(shape)==4:
     l=shape[2]
     m=shape[3]
    else:
     l=1
     m=1
    return [l,m]
   except:
    # no set, just a scalar
    # print "Scalar Return "
    return [1,1] 
  elif type=='Q':
   try:
    shape=self.__sQ.shape
    if len(shape)==4:
     l=shape[2]
     m=shape[3]
    else:
     l=1
     m=1
    return [l,m]
   except:
    # no set, just a scalar
    # print "Scalar Return "
    return [1,1] 
  elif type=='U':
   try:
    shape=self.__sU.shape
    if len(shape)==4:
     l=shape[2]
     m=shape[3]
    else:
     l=1
     m=1
    return [l,m]
   except:
    # no set, just a scalar
    # print "Scalar Return "
    return [1,1] 
  elif type=='V':
   try:
    shape=self.__sV.shape
    if len(shape)==4:
     l=shape[2]
     m=shape[3]
    else:
     l=1
     m=1
    return [l,m]
   except:
    # no set, just a scalar
    # print "Scalar Return "
    return [1,1] 

  # will not get here
  return [1,1]

 # returns the value(s) corresponding to the given (t,f) pair
 # and the quantity 'A','I','Q','U','V','RA','Dec'
 # note that in case of a patch, this would return a 2D
 # array in l,m coordinates
 def getVellsValue(self,type,freq_index,time_index):
  if (self.__lsm!=None) and (self.__lsm.cells!=None):
   my_cells=self.__lsm.cells
  elif self.__cells!=None:
   my_cells=self.__cells
  else:
   _dprint(0,"Cannot get Vells, please setup your meqserver proxy before you do this")
   return


  # range error check
  if (my_cells.segments.freq.start_index > freq_index) or\
    (my_cells.segments.freq.end_index < freq_index):
    _dprint(0,"Index error, Frequency %d",freq_index)
    freq_index=my_cells.segments.freq.start_index
  if (my_cells.segments.time.start_index > time_index) or\
    (my_cells.segments.time.end_index < time_index):
    _dprint(0,"Index error, Time %d",time_index)
    time_index=my_cells.segments.time.start_index

  if type=='A' or type=='I':
   # expect a vellset
   try:
    shape=self.__sI.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.__sI.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.__sI.value[0]
  elif type=='Q':
   # expect a vellset
   try:
    shape=self.__sQ.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.__sQ.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.__sQ.value[0]
  elif type=='U':
   # expect a vellset
   try:
    shape=self.__sU.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.__sU.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.__sU.value[0]
  elif type=='V':
   # expect a vellset
   try:
    shape=self.__sV.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.__sV.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.__sV.value[0]
  else:
    _dprint(0,"Error request %s",type)
    return 0


 # clone this Sixpack without circular reference to the LSM
 # and references to the MeqTree system for saving
 def clone(self):
  newsph=Sixpack(self.__name)
  newsph.__root=None
  #newsph.sI=self.sI
  #newsph.sQ=self.sQ
  #newsph.sU=self.sU
  #newsph.sV=self.sV
  #newsph.RA=self.RA
  #newsph.Dec=self.Dec
  return newsph

 # method to use object as a dictionary
 # to get 
 # 'root' : root node
 # 'radec': RADec root node
 # 'iquv' : IQUV root node
 def __getitem__(self,iname):
   if iname=='root':
    return self.__root
   elif iname=='radec':
    if self.__radec!=None:
     return self.__radec
    else:
     return None
   elif iname=='iquv':
    return self.__iquv
   else:
    return None

 # 
 def oneliner(self):
  s=TDL_common.Super.oneliner(self)
  s+="This is a Sixpack"
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
   temp_str+="}"
   return temp_str
