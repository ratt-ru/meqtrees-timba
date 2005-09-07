#!/usr/bin/env python

## Sixpack Object

from Timba.LSM.LSM import *
#from Timba.TDL import Settings
#from Timba.LSM.LSM_GUI import *
from Timba.Contrib.JEN import MG_JEN_sixpack
from Timba.Meq import meq

class Sixpack:
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
 # ns: NodeScope object
 # pname: unique name for the root of the subtree, 
 #    generally the name of the PUnit
 # I0_: Apparent Brightness
 # SI_: Spectral Index , needs to be an array
 # f0_: Frequency
 # RA_: Right Ascention
 # Dec_: Declination
 def __init__(self,pname=None,ns=None,I0_=0.0,SI_=[0.0],f0_=1e6,RA_=0.0,Dec_=0.0):
   self.__name=pname 
   self.__type='Sixpack'
   #remember the nodescope
   self.__ns=ns
   # create trees using JEN code, if there is a node scope
   if self.__ns !=None:
    tmp_sixpack=MG_JEN_sixpack.newstar_source(self.__ns,name=self.__name,I0=I0_, SI=SI_,f0=f0_,RA=RA_, Dec=Dec_,trace=0)
    self.__iquv=tmp_sixpack['iquv']
    self.__radec=tmp_sixpack['radec']
    # check whether we already have a node with given name
    if self.__ns[self.__name].initialized() !=True:
     self.__root=self.__ns[self.__name]<<Meq.Composer(self.__radec['RA'],self.__radec['Dec'],self.__iquv['StokesI'],self.__iquv['StokesQ'],self.__iquv['StokesU'],self.__iquv['StokesV'])
    else: # if this node has already being defined
     print "Node already defined"
     self.__root=None

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

 # return type
 def type(self):
  return self.__type

 # create the trees
 def createTree(self,**kw): 
  if kw.has_key('name'):
   self.__name=kw['name']
  if self.__ns!=None and self.__name !=None:
   if kw.has_key['I0']:
    I0_=kw['I0']
   else:
    I0=0.0
   if kw.has_key['SI']:
    SI_=kw['SI']
   else:
    SI_=[0]
   if kw.has_key['f0']:
    f0_=kw['f0']
   else:
    f0_=1e6
   if kw.has_key['RA']:
    RA_=kw['RA']
   else:
    RA_=0
   if kw.has_key['Dec']:
    Dec_=kw['Dec']
   else:
    Dec_=0
   tmp_sixpack=MG_JEN_sixpack.newstar_source(self.__ns,name=self.__name,I0=I0_, SI=SI_,f0=f0_,RA=RA_, Dec=Dec_,trace=0)

   self.__iquv=tmp_sixpack['iquv']
   self.__radec=tmp_sixpack['radec']
   # check whether we already have a node with given name
   if self.__ns[self.__name].initialized() !=True:
     self.__root=self.__ns[self.__name]<<Meq.Composer(self.__radec['RA'],self.__radec['Dec'],self.__iquv['StokesI'],self.__iquv['StokesQ'],self.__iquv['StokesU'],self.__iquv['StokesV'])
   else: # if this node has already being defined
     print "Node already defined"
     self.__root=None

 # update values according to the new cells, 
 # the name of the p-unit is given by 'pname'
 def updateValues(self,pname):
  if (self.__lsm!=None) and (self.__lsm.cells!=None) and\
   (self.__lsm.mqs!=None):
   my_cells=self.__lsm.cells
   my_mqs=self.__lsm.mqs
  elif self.__cells!=None and self.__mqs!=None:
   my_cells=self.__cells
   my_mqs=self.__mqs
  else:
   print "Cannot update values: (cell,mqs)"
   return

  # create request object
  my_request = meq.request(cells=my_cells, eval_mode=0)
  pname=self.__name
  # if name==None, get name from root
  if pname==None and self.__ns!=None:
   pname=self.__root.name
  my_args=meq.record(name=pname, request=my_request)
  my_result=my_mqs.meq('Node.execute', my_args,wait=True)
  #print my_result
  # update value
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
   print "Cannot update values: (cells,mqs)"
   return


  # range error check
  if (my_cells.segments.freq.start_index > freq_index) or\
    (my_cells.segments.freq.end_index < freq_index):
    print "Index error, Frequency %d" %freq_index
    freq_index=my_cells.segments.freq.start_index
  if (my_cells.segments.time.start_index > time_index) or\
    (my_cells.segments.time.end_index < time_index):
    print "Index error, Time %d" %time_index
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
   print "Cannot update values: (cell,mqs)"
   return


  # range error check
  if (my_cells.segments.freq.start_index > freq_index) or\
    (my_cells.segments.freq.end_index < freq_index):
    print "Index error, Frequency %d" %freq_index
    freq_index=my_cells.segments.freq.start_index
  if (my_cells.segments.time.start_index > time_index) or\
    (my_cells.segments.time.end_index < time_index):
    print "Index error, Time %d" %time_index
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
    print "Error request",type
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
  print "This is a Sixpack"

 def display(self):
  print str(self) 

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
