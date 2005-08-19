#!/usr/bin/python

# import modules for visualization
import sys
import pickle # for serialization and file io
from Dummy import *

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
  if (self.lsm!=None) and (self.lsm.cells!=None) and (self.lsm.mqs!=None):
   # create request object
   my_request = meq.request(cells=self.lsm.cells, eval_mode=0)
   my_args=meq.record(name=pname, request=my_request)
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

 # returns the value corresponding to the given (t,f) pair
 # and the quantity 'A','I','Q','U','V','RA','Dec'
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
  """
 # Constructor
 def __init__(self,name,lsm):
  # p-Unit name has to be a string
  if type(name) != type(""):
    raise TypeError,"Name must be a string, not %s"  % type(name).__name__
  self.name=name
  self.lsm=lsm
  self.type=0
  self.s_list=[]
  self.cat=1
  self.app_brightness=1
  self.sp=SpH(self.lsm)
  self.FOV_distance=0
 
 # change type (point: flag=0, patch: flag=1)
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

 # Print
 def __str__(self):
   temp_str="P-Unit: | Name="+str(self.name)
   temp_str+=", type="+str(self.type)
   temp_str+=",source_list="+str(self.s_list)
   temp_str+=",cat="+str(self.cat)
   temp_str+=",Brightness="+str(self.getBrightness())
   temp_str+=",sp="+str(self.sp)
   temp_str+=",FOV="+str(self.FOV_distance)
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
  newp.sp=self.sp.clone()
  newp.FOV_distance=self.FOV_distance
  return newp
 
 # set the LSM of this PUnit
 def setLSM(self,lsm):
  self.lsm=lsm
  self.sp.setLSM(lsm)

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
  # the ObsWin, just a cell right now
  self.cells=None

  self.__barr=[] 

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
     SP='Root of Sixpack'
     RA=100
     Dec=100
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

  if kw.has_key('type'):
   if kw['type']=='point':
    #FIXME: add POINT =0 PATCH=1 etc
    p.setType(0) # 0 - point source
  else:
   p.setType(1) # 1 - patch
  
  # set the root of sixpack helper
  if kw.has_key('SP'):
   p.sp.setRoot(kw['SP'])

#  # FIXME for the moment use static RA,Dec
  if kw.has_key('RA'):
   p.sp.set_staticRA(kw['RA'])
  if kw.has_key('Dec'):
   p.sp.set_staticDec(kw['Dec'])



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
 # return number of p-Units in the p-Unit table 
 def getPUnits(self):
  return len(self.p_table)
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

   p.dump(g)
   f.close()
  except Error:
   print "file %s cannot be opened, save failed" % filename 
  
  # next step: save the MeqTrees
  if self.mqs != None:
   forest_filename=filename+'.forest'
   self.mqs.meq('Save.Forest',meq.record(file_name=forest_filename));

 # load from a file 
 def load(self,filename):
  try:
   f=open(filename,'rb') 
   p=pickle.Unpickler(f)
   tmpl=LSM()
   tmpl=p.load()
   self.s_table=tmpl.s_table
   self.m_table=tmpl.m_table
   self.tmpl_table=tmpl.tmpl_table
   self.p_table=tmpl.p_table
   self.__barr=tmpl.__barr
   f.close()
  except IOError:
   print "file %s cannot be opened, load failed" % filename 
  # next step: Load the MeqTrees if possible 
  if self.mqs != None:
   forest_filename=filename+'.forest'
   self.mqs.meq('Load.Forest',meq.record(file_name=forest_filename),wait=True);


 # send a request to the LSM to give the p-units
 # with highest brightness, or p-unit with name ='name' etc.
 # returns a list of p-units satisfying the query
 def queryLSM(self,**kw):
  # possible query formats are:
  # count=4 : gives first 4 brightest punits
  # name='name': gives p unit matching name='name'
  # cat=1,2,.. : gives p units of given category
  
  output=[]
  if kw.has_key('name'):
   output.append(self.p_table(kw['name']))
   return output
  
  if kw.has_key('count'):
   for i in range(min(kw['count'],len(self.__barr))): 
    output.append(self.p_table[self.__barr[i]])
   return output

  if kw.has_key('cat'):
    for pname in self.p_table.keys():
     if self.p_table[pname].getCat()==kw['cat']:
       output.append(self.p_table[pname])
    return output
