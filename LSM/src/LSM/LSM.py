#!/usr/bin/python

# import modules for visualization
import sys
import pickle # for serialization and file io
from Dummy import *

from common_utils import *
from Timba.Meq import meq
from Timba.TDL import *
from Timba.Trees import TDL_Sixpack

#############################################
class Source:
 """Source object in source table
 Attributes are
 name=Source name - String
 treeType=type of Template tree - string
 tableName=MeqParm table Name - string"""

 # Constructor
 def __init__(self,name,treeType='Point1',tableName='Table1'):
   # Check source name to be a string
   if type(name) != type(""):
    raise TypeError,"Name must be a string, not %s"  % type(name).__name__
   self.name=name
   self.treeType=treeType
   self.tableName=tableName

 # set template tree type
 def setTemplateTree(self,treeType):
   self.treeType=treeType
 
 # Print
 def __str__(self):
   temp_str="Source name: "+self.name
   temp_str+=" Template tree: "+self.treeType
   temp_str+=" MeqParm Table: "+self.tableName
   return temp_str
###############################################
# class sixpack is not needed to be defined here (JEN code does that)
# instead we define a class to store a cell and six vellsets
# to store the request/response to the meqtree
# sixpack helper
class SpH:
 """the sixpack helper contains:
    root: root or the composer node of the six subtrees
    lsm: LSM using this sixpack - needed to obtain ObsWin and ObsRes info
    sI:
    sQ:
    sU:
    sV:
    RA:
    Dec: the six vellsets of the current response
 """
 
 # Constructor
 def __init__(self,lsm,Root=None,mqs=None,sI=None,sQ=None,sU=None,sV=None,RA=None,Dec=None):
  self.root=Root
  self.lsm=lsm
  self.sI=sI
  self.sQ=sQ
  self.sU=sU
  self.sV=sV
  self.RA=RA
  self.Dec=Dec
  # static value for debugging
  self.static_RA=0
  self.static_Dec=0

 # traditional getter and setter methods
 # setter methods need the vellset as input
 # getter methods return the value array
 def setI(self,I):
  self.sI=I
 def getI(self):
  if self.sI==None:
   return 0
  return self.sI.value
 def setQ(self,Q):
  self.sQ=Q
 def getQ(self):
  if self.sQ==None:
   return 0
  return self.sQ.value
 def setU(self,U):
  self.sU=U
 def getU(self):
  if self.sU==None:
   return 0
  return self.sU.value
 def setV(self,V):
  self.sV=V
 def getV(self):
  if self.sU==None:
   return 0
  return self.sV.value
 def setRA(self,RA):
  self.RA=RA
 def getRA(self):
  if self.RA==None:
   return self.static_RA
  return self.RA.value[0]
#  return self.static_RA
 def setDec(self,Dec):
  self.Dec=Dec 
 def getDec(self):
  if self.Dec==None:
   return self.static_Dec 
  return self.Dec.value[0]
#  return self.static_Dec

 ### Debugging
 def set_staticRA(self,RA):
  self.static_RA=RA
# def get_staticRA(self):
#  return self.static_RA
 def set_staticDec(self,Dec):
  self.static_Dec=Dec 
# def get_staticDec(self):
#  return self.static_Dec


 # setting the meqtree root
 def setRoot(self,root):
  self.root=root
 # link back to the LSM
 def setLSM(self,lsm):
  self.lsm=lsm

 # update values according to the new cell, 
 # the name of the p-unit is given by 'pname'
 def updateValues(self,pname):
  from Timba.Meq import meq
  if (self.lsm!=None) and (self.lsm.cells!=None) and\
   (self.lsm.mqs!=None):
   # create request object
   my_request = meq.request(cells=self.lsm.cells, eval_mode=0)
   my_args=meq.record(name='sixpack:q='+pname, request=my_request)
   my_result=self.lsm.mqs.meq('Node.execute', my_args,wait=True)
   #print my_result
   # update value
   self.setRA(my_result.result.vellsets[0])
   self.setDec(my_result.result.vellsets[1])
   self.setI(my_result.result.vellsets[2])
   self.setQ(my_result.result.vellsets[3])
   self.setU(my_result.result.vellsets[4])
   self.setV(my_result.result.vellsets[5])
  else:
   print "Cannot update values: (cell,mqs)",self.lsm.cells,self.lsm.mqs


 # returns the size of the values corresponding to the given (t,f) pair
 # and the quantity 'A','I','Q','U','V','RA','Dec'
 # returns [l,m] for lxm array size
 def getValueSize(self,type,freq_index,time_index):
  # range error check
  if (self.lsm.cells.segments.freq.start_index > freq_index) or\
    (self.lsm.cells.segments.freq.end_index < freq_index):
    print "Index error, Frequency %d" %freq_index
    freq_index=self.lsm.cells.segments.freq.start_index
  if (self.lsm.cells.segments.time.start_index > time_index) or\
    (self.lsm.cells.segments.time.end_index < time_index):
    print "Index error, Time %d" %time_index
    time_index=self.lsm.cells.segments.time.start_index
  if type=='A' or type=='I':
   # expect a vellset
   try:
    shape=self.sI.shape
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
    shape=self.sQ.shape
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
    shape=self.sU.shape
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
    shape=self.sV.shape
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
 def getValue(self,type,freq_index,time_index):
  # range error check
  if (self.lsm.cells.segments.freq.start_index > freq_index) or\
    (self.lsm.cells.segments.freq.end_index < freq_index):
    print "Index error, Frequency %d" %freq_index
    freq_index=self.lsm.cells.segments.freq.start_index
  if (self.lsm.cells.segments.time.start_index > time_index) or\
    (self.lsm.cells.segments.time.end_index < time_index):
    print "Index error, Time %d" %time_index
    time_index=self.lsm.cells.segments.time.start_index

  if type=='A' or type=='I':
   # expect a vellset
   try:
    shape=self.sI.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.sI.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.sI.value[0]
  elif type=='Q':
   # expect a vellset
   try:
    shape=self.sQ.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.sQ.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.sQ.value[0]
  elif type=='U':
   # expect a vellset
   try:
    shape=self.sU.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.sU.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.sU.value[0]
  elif type=='V':
   # expect a vellset
   try:
    shape=self.sV.shape
    if shape[0]==1:
     # no time dependence
     time_index=0
    if shape[1]==1:
     # no freq. dependence
     freq_index=0
    #print "Return ",self.sI.value[time_index][freq_index]
    return self.sV.value[time_index][freq_index]
   except:
    # no set, just a scalar
    #print "Scalar Return ",self.sI.value[0]
    return self.sV.value[0]
  else:
    print "Error request",type
    return 0




 
 # Print
 def __str__(self):
   temp_str="SPHelper: {I="+str(self.getI())
   temp_str+=",Q="+str(self.getQ())
   temp_str+=",U="+str(self.getU())
   temp_str+=",V="+str(self.getV())
   temp_str+=",RA="+str(self.getRA())
   temp_str+=",Dec="+str(self.getDec())
   temp_str+="}"
   return temp_str

 # clone this SpH without circular reference to the LSM
 # and references to the MeqTree system for saving
 def clone(self):
  newsph=SpH(None)
  newsph.root=None
  #newsph.sI=self.sI
  #newsph.sQ=self.sQ
  #newsph.sU=self.sU
  #newsph.sV=self.sV
  #newsph.RA=self.RA
  #newsph.Dec=self.Dec
  # static value for debugging
  newsph.static_RA=self.static_RA
  newsph.static_Dec=self.static_Dec
  return newsph


 
###############################################
class TemTree:
 """Template tree object"""
 
 # Constructor
 def __init__(self,id):
  self.id=id 

###############################################
class PUnit:
 """p-Unit object 
 Attributes are
  name: will be a unique string like "3C48" or "patch#23". Note source 
    names are also stored in source table.
  type: point soure/ patch - integer, 0 - point soure, 1 - patch
  s_list: source list - list of sources in the source table
  cat: 1 - source is Cat I, 2 - Cat 2, etc (default 1)
  app_brightness: apparent brightness - used in sorting and peeling
  sp: the sixpack helper object
   {Root, Cell, sI: sQ: sU: sV: RA: Dec: }
  FOV_distance: relative OBSWIN size
  lsm: LSM using this PUnit

  _patch_name: if this PUnit is a point source, and belongs to a patch,
     remember the name of the patch here. If this is a patch or a point
     source that does not belong to a patch, this value is None.

  __sixpack: store the sixpack object
  """
 # Constructor
 def __init__(self,name,lsm):
  # p-Unit name has to be a string
  if type(name) != type(""):
    raise TypeError,"Name must be a string, not %s"  % type(name).__name__
  self.name=name
  self.lsm=lsm
  self.type=POINT_TYPE
  self.s_list=[]
  self.cat=1
  self.app_brightness=1
  self.sp=SpH(self.lsm)
  self.FOV_distance=0

  self._patch_name=None # FIXME: only temporary

  self.__sixpack=None
 
 # change type (point: flag=POINT_TYPE, patch: flag=PATCH_TYPE)
 def setType(self,flag):
  self.type=flag
 # return type
 def getType(self):
  return self.type
  
 # add a source to the source list, s = source name
 def addSource(self,s):
  self.s_list.append(s)
 # return the source list
 def getSources(self):
  return self.s_list
 
 # change Category 
 def setCat(self,cat):
  self.cat=cat
 # return category
 def getCat(self):
  return self.cat

 # change apparent brightness
 def setBrightness(self,brightness):
  self.app_brightness=brightness

 # return value
 # type='I','Q','U','V' or 'A' for app_brightness
 # f=freq_index, t=time_index
 def getBrightness(self,type='A',f=0,t=0):
  if type=='A':
   return self.app_brightness
  else:
    return self.sp.getValue(type,f,t)

 # change FOV distance
 def setFOVDist(self,distance):
  self.FOV_distance=distance
 def getFOVDist(self):
  return self.FOV_distance


 # it this PUnit is a patch, return the limits
 # of its boundary
 # [x_min,y_min,x_max,y_max]
 def getLimits(self):
  if self.type != PATCH_TYPE:
    return [0,0,0,0]
  else:
   # traverse the source list 
   x_min=1e6
   y_min=1e6
   x_max=-1e6
   y_max=-1e6
   for sname in self.s_list:
    punit=self.lsm.p_table[sname]
    if punit != None:
     x=punit.sp.getRA()
     y=punit.sp.getDec()
     if x_min > x:
      x_min=x
     if x_max < x:
      x_max=x
     if y_min > y:
      y_min=y
     if y_max < y:
      y_max=y
   return [x_min,y_min,x_max,y_max]  
  # will not get here  
  return [0,0,0,0]

 # Print
 def __str__(self):
   temp_str="P-Unit: | Name="+str(self.name)
   temp_str+=", type="+str(self.type)
   temp_str+=",source_list="+str(self.s_list)
   temp_str+=",cat="+str(self.cat)
   temp_str+=",Brightness="+str(self.getBrightness())
   temp_str+=",sp="+str(self.sp)
   temp_str+=",FOV="+str(self.FOV_distance)
   temp_str+=",sixpack="+str(self.__sixpack)
   temp_str+=" |"
   return temp_str


 # clone the PUnit without circular references to the LSM
 # or references to MeqTree systems so that it can be saved
 def clone(self):
  newp=PUnit(self.name,None)
  newp.type=self.type
  newp.s_list=self.s_list
  newp.cat=self.cat
  newp.app_brightness=self.app_brightness
  # sixpack helper
  newp.sp=self.sp.clone()
  # instead of the Sixpack Object, we store the 
  # root node namse of the IQUV,Ra,Dec subtrees
  if self.__sixpack!=None:
   newp.__sixpack={}
   #print self.__sixpack
   if self.__sixpack.ispoint():
    newp.__sixpack['I']=self.__sixpack.stokesI().name
    newp.__sixpack['Q']=self.__sixpack.stokesQ().name
    newp.__sixpack['U']=self.__sixpack.stokesQ().name
    newp.__sixpack['V']=self.__sixpack.stokesV().name
    newp.__sixpack['ra']=self.__sixpack.ra().name
    newp.__sixpack['dec']=self.__sixpack.dec().name
    newp.__sixpack['label']=self.__sixpack.label()
    newp.__sixpack['pointroot']=self.__sixpack.sixpack().name
   else:
    newp.__sixpack['patchroot']=self.__sixpack.root().name
    newp.__sixpack['label']=self.__sixpack.label()
  else:
   newp.__sixpack=None
  newp.FOV_distance=self.FOV_distance
  newp._patch_name=self._patch_name
  return newp
 
 # set the LSM of this PUnit
 def setLSM(self,lsm):
  self.lsm=lsm
  self.sp.setLSM(lsm)

 # set the sixpack object
 def setSP(self,sp):
  self.__sixpack=sp
 # return a sixpack object (TDL_Sixpack) for this PUnit
 def getSP(self):
  return self.__sixpack

###############################################
class LSM:
 """LSM Object:
 Attributes are
  s_table: Source table
  m_table: MeqParm table
  tmpl_table: Template tree table
  p_table: p-Unit table

  helper attributes:
  __barr: array of p-Units sorted by brightness - private attribute
  __mqs: meqserver proxy
 """
 # Constructor
 # Does pretty much nothing so far
 def __init__(self):
  self.s_table={}
  self.m_table={}
  self.tmpl_table={}
  self.p_table={}
  self.mqs=None
  # the request domain, just a cell right now
  self.cells=None
  # need to remember the forest
  self.__ns=None
  # counter to give unique names to patches
  self.__patch_count=0
 
  self.__barr=[] 
  # root of all subtrees
  self.__root=None

 # Much more important method
 # Inserts a source to source table
 def add_source(self,s, **kw):
  """This will insert source s to stable,
    and search the MeqParm table for the params of the source
    (using the source name). Then will add relevent params from
    the mtable (row numbers) to the source param list
    Arguments:
    s: Source object
    **kw=variable list of keyword arguments such as
     brightness=10
     type='point' / 'patch'
     sixpack='Sixpack object, in a composed state'
     ra=100
     dec=100
  """ 
  # Source names have to be unique
  if self.s_table.has_key(s.name):
   # Print error
   raise NameError, 'Source '+s.name+' is already present'
  self.s_table[s.name]=s
  """ After inserting the source to source table,
      search the  MeqParm table if it has any parms of the source.
     Add these params to the source param list."""

  """Now create a p-unit object for this (point) source.
      the p-unit object will link to the template trees.
      Note that p-unit table has to be sorted by brightness.
      so the insertion has to done in a sorted way.
  """
  # Use the p-unit name to be the source name (point source) 
  p=PUnit(s.name,self)
  # add the source to the source list of the p-unit
  p.addSource(s.name)
  
  # all other p-Unit parameters are given be key-word argument list
  if kw.has_key('brightness'):
   p.setBrightness(kw['brightness'])
  else:
   p.setBrightness(0)

  if kw.has_key('type') and \
    kw['type']=='patch':
    #add POINT =0 PATCH=1 etc
    p.setType(PATCH_TYPE) # 1 - patch
  else:
    p.setType(POINT_TYPE) # 0 - point source
  
  # set the sixpack object
  if kw.has_key('sixpack'):
   p.setSP(kw['sixpack'])
   # set the root
   my_sixpack=p.getSP()
   p.sp.setRoot(my_sixpack.sixpack())


#  # FIXME for the moment use static RA,Dec
  if kw.has_key('ra'):
   p.sp.set_staticRA(kw['ra'])
  if kw.has_key('dec'):
   p.sp.set_staticDec(kw['dec'])



  # finally, insert p-Unit to p-Unit table
  self.insertPUnit(p)

 # Helper method 
 # inserts a p-unit into the p-Unit table, and 
 # orders according to the brightness
 def insertPUnit(self,p):
  if self.p_table.has_key(p.name):
   raise NameError, 'PUnit '+p.name+' is already present'
  else:
   self.p_table[p.name]=p
  # now do the sorting of the brightness array
  tmp_brightness=p.getBrightness() 
  if (len(self.__barr)==0):
   self.__barr.insert(0,p.name)
  else: # list is not empty
   for i in range(len(self.__barr)):
    if self.p_table[self.__barr[i]].getBrightness() < tmp_brightness:
     break


   # special check for end of list
   if i==0: 
    if self.p_table[self.__barr[i]].getBrightness() < tmp_brightness:
      self.__barr.insert(0,p.name)
    else:
      self.__barr.append(p.name)
   elif i==len(self.__barr)-1:
    if self.p_table[self.__barr[i]].getBrightness() < tmp_brightness:
     self.__barr.insert(i,p.name)
    else:
     self.__barr.append(p.name)
   else:
    self.__barr.insert(i,p.name)

 # method for printing to screen
 def dump(self):
  print "---------------------------------"
  print "Source Table:"
  for s in self.s_table.keys():
   print self.s_table[s]
  print "\n\n"
  print "P-Unit Table:\n"
  for p in self.p_table.keys():
   print self.p_table[p]
  print "\n\n"

  print "P-Units sorted in Brightness:\n"
  for p in self.__barr:
   print p, self.p_table[p].getBrightness()

  print "---------------------------------"

 # set the MeqServer Proxy
 def setMQS(self,mqs):
  self.mqs=mqs

 # set the Cells for the request
 def setCells(self,cells):
  self.cells=cells

 # get the range of ObsWin
 # [f0,f1,fstep,t0,t1,tstep]
 def getCellsRange(self):
  res={}
  if self.cells != None:
   res['f0']=self.cells.domain.freq[0]
   res['f1']=self.cells.domain.freq[1]
   res['fstep']=self.cells.segments.freq.end_index+1
   res['t0']=self.cells.domain.time[0]
   res['t1']=self.cells.domain.time[1]
   res['tstep']=self.cells.segments.time.end_index+1

  return res

 # method for visualization
 # app='create' will create own QApplication.
 # when NOT using MeqBrowser, use this option
 def display(self, **kw ):
  d=Dummy(self,sys.argv)
  if kw.has_key('app') and (kw['app']=='create'):
    d.display(app='create')
  else:
    d.display()

 # return number of sources
 def getSources(self):
  return len(self.s_table)
 # return no of columes in source table
 def getSourceColumns(self):
  return 3
 # return the named p-Unit from the p-Unit table 
 def getPUnit(self,pname):
  if self.p_table.has_key(pname):
   return self.p_table[pname]
  # else
  return None 

 # return number of p-Units in the p-Unit table 
 def getPUnits(self):
  # do not count points that belong to a PUnit
  count=0
  for pname in self.p_table.keys():
   if self.p_table[pname]._patch_name ==None:
    count+=1
  return count 

 # return no of columes in p-Unit table
 def getPUnitColumns(self):
  return 12
 # return max,min values of RA and Dec
 def getBounds(self):
  max_RA=-100
  min_RA=100
  max_Dec=-100
  min_Dec=100

  for p in self.p_table.keys():
   punit=self.p_table[p]
   if punit.getType()==POINT_TYPE:
    tmpval=punit.sp.getRA()
    if tmpval > max_RA:
     max_RA=tmpval
    if tmpval <  min_RA:
     min_RA=tmpval
    tmpval=punit.sp.getDec()
    if tmpval > max_Dec:
     max_Dec=tmpval
    if tmpval <  min_Dec:
     min_Dec=tmpval
  result={}
  result['min_RA']=min_RA 
  result['max_RA']=max_RA 
  result['min_Dec']=min_Dec
  result['max_Dec']=max_Dec

  return result

 # return max value of (brightness)
 # type='I','Q','U','V' or 'A' for app_brightness
 # f=freq_index, t=time_index
 def getMaxBrightness(self,type='A',f=0,t=0):
  if type=='A':
   if len(self.__barr)==0:
    return 0
   pname=self.__barr[0]
   return self.p_table[pname].getBrightness()
  else:
   # select the max value
   tmp_max=0
   for pname in self.p_table.keys():
    if self.p_table[pname].getType()==POINT_TYPE:
     tmp_val=self.p_table[pname].sp.getValue(type,f,t)
     if tmp_max < tmp_val:
      tmp_max=tmp_val
   return tmp_max

  # else
  return 0

 # return min value of (brightness)
 # type='I','Q','U','V' or 'A' for app_brightness
 # f=freq_index, t=time_index
 def getMinBrightness(self,type='A',f=0,t=0):
  if type=='A':
   if len(self.__barr)==0:
    return 0
   pname=self.__barr[len(self.__barr)-1]
   return self.p_table[pname].getBrightness()
  else:
   # select the min value
   tmp_min=1000
   for pname in self.p_table.keys():
    if self.p_table[pname].getType()==POINT_TYPE:
     tmp_val=self.p_table[pname].sp.getValue(type,f,t)
     if tmp_min > tmp_val:
      tmp_min=tmp_val
   return tmp_min

  # else
  return 0

 # return current frequency and time
 def getCurrentFreqTime(self,freq_index,time_index):
  if self.cells==None:
   return [0,0]
  if (self.cells.segments.freq.start_index > freq_index) or\
    (self.cells.segments.freq.end_index < freq_index):
    print "get Curr Index error, Frequency %d" %freq_index
    freq_index=self.cells.segments.freq.start_index
  if (self.cells.segments.time.start_index > time_index) or\
    (self.cells.segments.time.end_index < time_index):
    print "get Curr Index error, Time %d" %time_index
    time_index=self.cells.segments.time.start_index

  f=self.cells.grid.freq[freq_index]
  t=self.cells.grid.time[time_index]
  return [f,t]


 # update vellset values for the current cells
 def updateCells(self):
  for sname in self.p_table.keys(): 
   punit=self.p_table[sname]
   #if punit.getType()==POINT_TYPE:
   punit.sp.updateValues(sname)

 # save to a file
 # while saving, discard any existing vellsets because
 # they can be recalculated. 
 def save(self,filename):
  try:
   f=open(filename,'wb') 
   p=pickle.Pickler(f)
   # create a new LSM from this LSM,
   # without reference to MeqServer or the forests
   g=LSM()
   g.s_table=self.s_table
   g.m_table=self.m_table
   g.tmpl_table=self.tmpl_table
   g.__barr=self.__barr
   # remove circular references to the old LSM
   g.p_table={}
   for sname in self.p_table.keys(): 
    punit=self.p_table[sname]
    g.p_table[sname]=punit.clone()
    g.p_table[sname].setLSM(g)
   g.mqs=None
   g.cells=None
   g.__patch_count=self.__patch_count


   # serialize the root
   if self.__root!=None:
    gdict={}
    self.traverse(self.__root,gdict)
    g.__root=pickle.dumps(gdict)
   else:
    g.__root=None
   p.dump(g)
   f.close()
  except IOError:
   print "file %s cannot be opened, save failed" % filename 
  
  # next step: save the MeqTrees
  if self.mqs != None:
   forest_filename=filename+'.forest'
   self.mqs.meq('Save.Forest',meq.record(file_name=forest_filename));

 # load from a file 
 def load(self,filename,ns=None):
  try:
   f=open(filename,'rb') 
   p=pickle.Unpickler(f)
   tmpl=LSM()
   tmpl=p.load()
   self.s_table=tmpl.s_table
   self.m_table=tmpl.m_table
   self.tmpl_table=tmpl.tmpl_table
   self.__barr=tmpl.__barr

   self.__patch_count=tmpl.__patch_count
   if tmpl.__root!=None:
    if ns==None:
     ns=NodeScope()
    self.__ns=ns
    my_dict=pickle.loads(tmpl.__root)
    self.__root=self.reconstruct(my_dict,ns)
    self.__ns.Resolve()
   else:
     self.__root=None

   self.p_table=tmpl.p_table
   # reconstruct PUnits and Sixpacks if possible
   for sname in self.p_table.keys(): 
    punit=self.p_table[sname]
    punit.setLSM(self)
    # now create the sixpack
    tmp_dict=punit.getSP()
    #print tmp_dict
    if tmp_dict.has_key('patchroot'):
     my_sp=TDL_Sixpack.Sixpack(label=tmp_dict['label'],\
      ns=self.__ns, root=self.__ns[tmp_dict['patchroot']])
    else: 
     # NOTE: do not give the nodescope because then it tries to
     # compose, but the tree is already composed
     my_sp=TDL_Sixpack.Sixpack(label=tmp_dict['label'],\
       ra=self.__ns[tmp_dict['ra']],\
       dec=self.__ns[tmp_dict['dec']],stokesI=self.__ns[tmp_dict['I']],\
       stokesQ=self.__ns[tmp_dict['Q']],stokesU=self.__ns[tmp_dict['U']],\
      stokesV=self.__ns[tmp_dict['V']])
     # set the root node
     my_sp=my_sp.clone(sixpack=self.__ns[tmp_dict['pointroot']],ns=self.__ns)

    punit.setSP(my_sp)
    # set the root
    punit.sp.setRoot(my_sp.sixpack())


   f.close()
  except IOError:
   print "file %s cannot be opened, load failed" % filename 
  # next step: Load the MeqTrees if possible 
  if self.mqs != None:
   forest_filename=filename+'.forest'
   #self.mqs.meq('Load.Forest',meq.record(file_name=forest_filename),wait=True);
   self.mqs.meq('Load.Forest',meq.record(file_name=forest_filename));


 # send a request to the LSM to give the p-units
 # with highest brightness, or p-unit with name ='name' etc.
 # returns a list of p-units satisfying the query
 def queryLSM(self,**kw):
  # possible query formats are:
  # count=4 : gives first 4 brightest punits
  # name='name': gives p unit matching name='name'
  # cat=1,2,.. : gives p units of given category
  
  outlist=[]
  if kw.has_key('name'):
   outlist.append(self.p_table[kw['name']])
   return outlist
  
  if kw.has_key('count'):
   for i in range(min(kw['count'],len(self.__barr))): 
    outlist.append(self.p_table[self.__barr[i]])
   return outlist

  if kw.has_key('cat'):
    for pname in self.p_table.keys():
     if self.p_table[pname].getCat()==kw['cat']:
       outlist.append(self.p_table[pname])
    return outlist


 # from the given list of (point) source  names (slist),
 # create a patch, and add it to the PUnit table
 # if calling this in a batchwise manner, call this with
 # resolve_forst=False and sync_kernel=False
 # in all calls but the last one, to speed things up
 def createPatch(self,slist,resolve_forest=True,sync_kernel=True):
  # first browse the slist and 
  # remove any sources already in a patch,
  # also calculate min,max of (RA,Dec) to find the 
  # phase center of the patch.
  x_min=1e6
  x_max=-1e6
  y_min=1e6
  y_max=-1e6
  correct_slist=[]
  sum_brightness=0
  for sname in slist:
    # select only sources without a patch 
    if (self.p_table.has_key(sname) and\
       self.p_table[sname]._patch_name ==None):
      correct_slist.append(sname)
      # remove this source from sorted patch list
      self.__barr.remove(sname)
      # get min,max coords
      ra=self.p_table[sname].sp.getRA() 
      dec=self.p_table[sname].sp.getDec() 
      if ra>x_max:
       x_max=ra
      if ra<x_min:
       x_min=ra
      if dec>y_max:
       y_max=dec
      if dec<y_min:
       y_min=dec
      # get apparent brightness of this source
      sum_brightness+=self.p_table[sname].getBrightness()

  #print "Patch: [%f,%f]--[%f,%f]"%(x_min,y_min,x_max,y_max)
  #print correct_slist
  #print self.__ns
  if self.__ns!=None and (len(correct_slist)> 0):
   patch_name='patch'+str(self.__patch_count)
   self.__patch_count=self.__patch_count+1
   stringRA='ra0:q='+patch_name
   meq_polc=meq.polc((x_min+x_max)*0.5)
   RA_root=self.__ns[stringRA]<<Meq.Parm(meq_polc)
   stringDec='dec0:q='+patch_name
   meq_polc=meq.polc((y_min+y_max)*0.5)
   Dec_root=self.__ns[stringDec]<<Meq.Parm(meq_polc) 
   # twopack for phase center
   twoname='radec:q='+patch_name
   tworoot=self.__ns[twoname]<<Meq.Composer(RA_root,Dec_root)
  
   child_list=[twoname]
   # get the sixpack root of each source in slist
   # and add it to patch composer
   for sname in correct_slist:
     child_list.append('sixpack:q='+sname)
     self.p_table[sname]._patch_name=patch_name

   patch_root=self.__ns['sixpack:q='+patch_name]<<Meq.PatchComposer(children=child_list)

   # add this to our root
   self.addToTree(patch_root)

   #patch_root=self.__ns[patch_name]<<Meq.Composer(children=child_list)
   #select_root=self.__ns['Select['+patch_name+']']<<Meq.Selector(children=patch_root,multi=True,index=[2,3,4,5])
   #stokes_root=self.__ns['Stokes['+patch_name+']']<<Meq.Stokes(children=select_root)
   #fft_root=self.__ns['FFT['+patch_name+']']<<Meq.FFTBrick(children=stokes_root)
   if self.__ns != None and resolve_forest==True:
    self.__ns.Resolve()
    #print "Current forest has %d root nodes, of a total of %d nodes"% (len(self.__ns.RootNodes()),len(self.__ns.AllNodes()))

   #Timba.TDL._dbg.set_verbose(5);
   # try to run stuff
   if self.mqs != None and resolve_forest==True and\
      sync_kernel==True:
     self.mqs.meq('Clear.Forest')
     self.mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),self.__ns.AllNodes().itervalues())));
     self.mqs.meq('Resolve.Batch',record(name=list(self.__ns.RootNodes().iterkeys())))
     # is a forest state defined?
     fst = getattr(Timba.TDL.Settings,'forest_state',record());
     self.mqs.meq('Set.Forest.State',record(state=fst));

   # create a new PUnit
   newp=PUnit(patch_name,self)
   newp.setType(PATCH_TYPE)
   newp.sp.setRoot(patch_root)
   newp.setBrightness(sum_brightness)
   # update vellsets
   if resolve_forest==True and sync_kernel==True:
    newp.sp.updateValues(patch_name)
   #from Timba.Meq import meq
   #ftdom=meq.domain(startfreq=1e6, endfreq=3e6, starttime=0,endtime=1)
   #cc=meq.cells(domain=ftdom,num_freq=2, num_time=1)
   #req=meq.request(cells=cc,eval_mode=0)
   #args=meq.record(name=patch_name,request=req)
   #aa=self.mqs.meq('Node.execute',args,wait=True)
   for sname in correct_slist:
     newp.addSource(sname)

   # this PUnit is a Patch, so the traditional TDL_Sixpack
   # object does not apply here. However, we will create a dummy 
   # sixpack object.

   newp.setSP(TDL_Sixpack.Sixpack(root=patch_root,label=patch_name))
   # add new PUnit to table
   self.insertPUnit(newp)
   #print self.__barr
   #self.p_table[patch_name]=newp

   #Timba.TDL._dbg.set_verbose(0);
   # return [patch name, x_min,y_min,x_max,y_max]
   # for the plotting method
   return [patch_name,x_min,y_min,x_max,y_max]

  # if we get here, an error
   return None


 # create patches from the grid, given by
 # an x_arry and y_array of grid points
 # note: x_array and y_array should be sorted in ascending order
 def createPatchesFromGrid(self,x_array,y_array,min_bright=0.0,max_bright=10.0,\
           min_sources=10):
  #from Timba.utils import verbosity
  #_dbg = verbosity(0,name='LSM')
  #_dprint = _dbg.dprint
  #_dprint(3,"Creating patches for",x_array,y_array)

  # add a margin to last elements to include points on the boundary
  x_array[len(x_array)-1]+=0.00001
  y_array[len(y_array)-1]+=0.00001

  # encapsulate arrays with large bounds
  # so we do not miss any points
  x_array.insert(0,x_array[0]-1e6)
  x_array.append(x_array[len(x_array)-1]+1e6)
  y_array.insert(0,y_array[0]-1e6)
  y_array.append(y_array[len(y_array)-1]+1e6)

  #print x_array
  #print y_array

  # now for each point source in p-unit list
  # if they are not already included in a patch
  # and also if they satisfy the criteria for including
  # in a patch, do a binary search and find correct grid position
  
  # set up bins to collect sorted sources
  xbins={}
  for ii in range(len(x_array)-1):
   xbins[ii]=[]
  ybins={}
  for ii in range(len(y_array)-1):
   ybins[ii]=[]

  #print xbins
  #print ybins
  for sname in self.p_table.keys(): 
    punit=self.p_table[sname]
    pb=punit.getBrightness('A')
    if  punit.getType()==POINT_TYPE and\
       punit._patch_name==None and\
       (pb<=max_bright) and (pb>=min_bright):
      # get RA and Dec
      xx=punit.sp.getRA()
      yy=punit.sp.getDec()
      k=bin_search(x_array,xx,0,len(x_array)-1)
      xbins[k].append(sname)
      k=bin_search(y_array,yy,0,len(y_array)-1)
      ybins[k].append(sname)

  #print xbins
  #print ybins
  # now create a reverse mapping hash table
  # indexed by source name, such that the pair
  # of indices [x_,y_] for each source (patch index)
  # is given
  p_id_x={}
  p_id_y={}
  # ignore bin indices 0 and the last_index
  # bacause these fall out of the range
  if len(xbins)>2:
   for ii in range(len(xbins)-2):
    ll=xbins[ii+1]
    # traverse list
    for sname in ll:
      p_id_x[sname]=ii+1
  if len(ybins)>2:
   for ii in range(len(ybins)-2):
    ll=ybins[ii+1]
    # traverse list
    for sname in ll:
      p_id_y[sname]=ii+1

  #print p_id_x
  #print p_id_y

  # now create the patches
  patch_bins={}
  for ii in range(len(xbins)-2):
   for jj in range(len(ybins)-2):
    patch_name="Patch#"+str(ii+1)+":"+str(jj+1)
    patch_bins[patch_name]=[]
 
  for sname in p_id_x.keys():
    ii=p_id_x[sname]
    if p_id_y.has_key(sname):
     jj=p_id_y[sname]
     patch_name="Patch#"+str(ii)+":"+str(jj)
     patch_bins[patch_name].append(sname)

  #print patch_bins
  # now call single patch creation function
  # remember return values from single patch creation
  retval_arr=[]
  new_punit_names=[]
  for pname in patch_bins.keys():
   # note: we do not send anything to the kernel
   # when we recreate the forest, that will be done later
   if len(patch_bins[pname]) >= min_sources:
    retval=self.createPatch(patch_bins[pname],True,False)
   else:
    retval=None

   if retval !=None:
    retval_arr.append(retval)
    # remember PUnit name to update its value
    new_punit_names.append(retval[0])
  # now resolve forest and sync kernel
  self.__ns.Resolve()
  #print "Resolved local NodeScope"
  #print "Current forest has %d root nodes, of a total of %d nodes"% (len(self.__ns.RootNodes()),len(self.__ns.AllNodes()))
  if self.mqs != None:
     #print "Sending request to kernel"
     self.mqs.meq('Clear.Forest')
     self.mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),self.__ns.AllNodes().itervalues())));
     self.mqs.meq('Resolve.Batch',record(name=list(self.__ns.RootNodes().iterkeys())))
     # is a forest state defined?
     fst = getattr(Timba.TDL.Settings,'forest_state',record());
     self.mqs.meq('Set.Forest.State',record(state=fst));
     # update vellset values for all newly created PUnits
     for pname in new_punit_names:
      print "Updating Punit ",pname
      punit=self.getPUnit(pname)
      punit.sp.updateValues(pname)



  return retval_arr


 # set the current NodeScope
 def setNodeScope(self,ns):
  self.__ns=ns
  # create a single root not to accomodate all subtrees
  # in the PUnit table
  child_list=[]
  for pname in self.p_table.keys():
   punit=self.getPUnit(pname)
   if punit.sp!=None:
    child_list.append('sixpack:q='+pname)
  # create a common root
  if len(child_list)!=0:
   self.__root=self.__ns['lsmroot']<<Meq.Composer(children=child_list)


 # add a child node (subtree) to the root node
 def addToTree(self,child):
  if(self.__root!=None):
   self.__root.add_children(child)

 # return the current NodeScope
 def getNodeScope(self,ns):
  return self.__ns

 # the following methods are used to 
 # serialize trees by brute force. In fact,
 # no serialization is done, but only the essence required
 # to recreate the whole tree is stored as (recursive) dictionaries.
 def rec_parse(self,myrec):
  """ recursively parse init record 
      and construct a dictionary
  """
  #print myrec
  my_keys=myrec.keys()
  new_dict={}
  for kk in my_keys:
   if isinstance(myrec[kk],meq.record):
     new_dict[kk]=self.rec_parse(myrec[kk])
   elif isinstance(myrec[kk],numarray.numarraycore.NumArray): # meq.array
     #print myrec[kk].__class__
     if (myrec[kk].size()>1):
      new_dict[kk]=myrec[kk].tolist()
     else: # size 1 array
      new_dict[kk]=myrec[kk]
   else:
     new_dict[kk]=myrec[kk]
  return new_dict

 def traverse(self,root,node_dict):
  chlist=root.children
  name=root.name
  classname=root.classname
  if not node_dict.has_key(name):
   node_dict[name]={'name':name, 'classname':classname, 'initrec':{},\
        'children':[]}  
   ir=root.initrec()
   myrec=node_dict[name]
   myrec['initrec']=self.rec_parse(ir)
   #print node_dict[name]
   # if any children, traverse
   for idx,ch in chlist:
    self.traverse(ch,node_dict)
    myrec['children'].append(ch.name)

 def create_node_stub(self,mydict,stubs,ns,myname):
  myrec=mydict[myname]
  # first, if this node has any children
  # and if they have not being created,
  # create them
  chlist=myrec['children']
  stublist=[]
  for ch in chlist:
   if not stubs.has_key(ch):
    stubs[ch]=self.create_node_stub(mydict,stubs,ns,ch)
   stublist.append(stubs[ch])
  # now we have created the child list
  # now deal with initrec()
  irec=myrec['initrec']
  #print 'My Rec==',myrec
  #print 'Init Rec==',irec
  myclass=myrec.pop('classname')
  fstr="ns['"+myname+"']<<Meq."+myclass.lstrip('Meq')+'(children='+str(chlist)+','
  irec_str=""
  # Remove JUNK! from initrecord()
  # remove class field
  if irec.has_key('class'):
   irec.pop('class')
  # remove node_desctiption
  if irec.has_key('node_description'):
   irec.pop('node_description')
  # remove name
  if irec.has_key('name'):
   irec.pop('name')
  # remove children
  if irec.has_key('children'):
   irec.pop('children')



  for kname in irec.keys():
   krec=irec[kname]
   if not isinstance(krec,dict):
    irec_str=irec_str+" "+kname+"="+str(krec)+','
   else:
    if (kname=='default_funklet'):
     #print krec['coeff']
     irec_str=irec_str+" "+kname+"=meq.array("+str(krec['coeff'])+'),'

  total_str=fstr+irec_str+')'
  #print "Total=",total_str
  exec total_str in globals(),locals()
  return ns[myname]
     
 
 # the basic assumption with the following method is 
 # the forest has no circular references
 def reconstruct(self,my_dict,ns):
  # temp dictionary to store created node stubs
  nodestub_dict={}
  for sname in my_dict.keys():
   if not nodestub_dict.has_key(sname):
     nodestub_dict[sname]=self.create_node_stub(my_dict,nodestub_dict,ns,sname)


#########################################################################
