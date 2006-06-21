
#% $Id$ 

#
# Copyright (C) 2006
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

script_name = 'MG_SBY_save_tree.py'

# Short description:
# shows how to save/load a tree, without using
# the MeqBrowser


# History:
# Creation: Wed Oct 19 19:06:11 CEST 2005

# Copyright: The MeqTree Foundation 

# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq
import pickle
import sys
import numarray


#=====================================================================
#=====================================================================
def _define_forest (ns):
  # create a random tree, save it.
  ns1=NodeScope()
  ns1.f<<Meq.Parm(meq.polclog([1,0.1,0.01]))
  ns1.t<<Meq.Parm(meq.polc([0.01,0.1,1]))
  stubI=ns1['Istub']<<1.1*Meq.Sin(ns1.f+ns1.t)
  stubQ=ns1['Qstub']<<2.0*Meq.Cos(ns1.f)
  stubU=ns1['Ustub']<<2.1*Meq.Sin(ns1.f-2)
  stubV=ns1['Vstub']<<2.1*Meq.Cos(ns1.f-2)
  stubRA=ns1['RAstub']<<2.1*Meq.Cos(ns1.f-2)*Meq.Sin(ns1.t)
  stubDec=ns1['Decstub']<<2.1*Meq.Cos(ns1.f-2)*Meq.Sin(ns1.t)

  root=ns1.root<<Meq.Composer(stubI,stubQ,stubU,stubV,stubRA,stubDec)
  #save tree
  _save_tree(root,script_name+".saved") 
  # load tree
  _load_tree(ns,script_name+".saved")
  ns.Resolve()

#=====================================================================
#=====================================================================
################################
### Test forest,
def _test_forest (mqs, parent):
  ns1=NodeScope()
  # load the tree
  _load_tree(ns1,script_name+".saved")
  ns1.Resolve()

###################################################################
###### importable functions
def _save_tree(root,out_filename="mytree.saved"):
   """ Saves the tree given by its root
     to the filname."""
   f=open(out_filename,'wb')
   p=pickle.Pickler(f)
   ser_root={}
   traverse(root,ser_root)
   p.dump(ser_root)
   f.close()

def _load_tree(ns,in_filename="mytree.saved"):
   """Loads the tree saved in the in_filename 
     and builds it using the nodescope ns.
     returns the root of the tree"""
   f=open(in_filename,'rb')
   p=pickle.Unpickler(f)
   ser_root=p.load()
   root=reconstruct(ser_root,ns)
   f.close()


###############################################################
# the following methods are used to 
# serialize trees by brute force. In fact,
# no serialization is done, but only the essence required
# to recreate the whole tree is stored as (recursive) dictionaries.
def rec_parse(myrec):
  """ recursively parse init record 
      and construct a dictionary
  """
  #print myrec
  my_keys=myrec.keys()
  new_dict={}
  for kk in my_keys:
   if kk=='default_funklet':
     ff=myrec[kk]
     if is_meqpolclog(ff):
       #print "create polclog"
       gg={'type':'meqpolclog', 'funk':serialize_funklet(ff)}
     else:
       gg={'type':'meqpolc', 'funk':serialize_funklet(ff)}
    
     #print gg
     new_dict[kk]=gg
   elif isinstance(myrec[kk],meq.record):
     new_dict[kk]=rec_parse(myrec[kk])
   elif isinstance(myrec[kk],numarray.numarraycore.NumArray): # meq.array
     # just serialize the value
     #new_dict[kk+'_isarray']=pickle.dumps(myrec[kk])
     #print myrec[kk].__class__
     #print pickle.dumps(myrec[kk])
     new_dict[kk]=myrec[kk]
   else:
     new_dict[kk]=myrec[kk]
  return new_dict

def traverse(root,node_dict):
  chlist=root.children
  name=root.name
  classname=root.classname
  if not node_dict.has_key(name):
   node_dict[name]={'name':name, 'classname':classname, 'initrec':{},\
        'children':[]}  
   ir=root.initrec()
   #print ir
   myrec=node_dict[name]
   myrec['initrec']=rec_parse(ir)
   #print node_dict[name]
   # if any children, traverse
   for idx,ch in chlist:
    traverse(ch,node_dict)
    myrec['children'].append(ch.name)

def create_node_stub(mydict,stubs,ns,myname):
  myrec=mydict[myname]
  # first, if this node has any children
  # and if they have not being created,
  # create them
  chlist=myrec['children']
  #stublist=[]
  for ch in chlist:
   if not stubs.has_key(ch):
    stubs[ch]=create_node_stub(mydict,stubs,ns,ch)
  # stublist.append(stubs[ch])
  # now we have created the child list
  # now deal with initrec()
  irec=myrec['initrec']
  #print 'My Rec==',myrec
  #print 'Init Rec==',irec
  myclass=myrec.pop('classname')
  mygentype=myclass.replace("Meq","")
  if len(chlist)>0:
   fstr="ns['"+myname+"']<<Meq."+mygentype+'(children='+str(chlist)+','
  else:
   fstr="ns['"+myname+"']<<Meq."+mygentype+'('
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
     if krec['type']=='meqpolclog':
      irec_str=irec_str+" "+"meq.polclog(default_funklet_value),"
      # deserialize the value
      default_funklet_value=krec['funk']
      #print dir(default_funklet_value)
     else:# assume to be a meqpolc()
      irec_str=irec_str+" "+"meq.polc(default_funklet_value),"
      # deserialize the value
      default_funklet_value=krec['funk']
     #print default_funklet_value


  total_str=fstr+irec_str+')'
  # MeqParm is special
  #if myclass.lstrip('Meq')=='Parm':
  # total_str="ns['"+myname+"']<<Meq.Parm(default_funklet_value)"
  #print "Total=",total_str
  exec total_str in globals(),locals()
  return ns[myname]
     
 
# the basic assumption with the following method is 
# the forest has no circular references
def reconstruct(my_dict,ns):
  # temp dictionary to store created node stubs
  nodestub_dict={}
  for sname in my_dict.keys():
   if not nodestub_dict.has_key(sname):
     nodestub_dict[sname]=create_node_stub(my_dict,nodestub_dict,ns,sname)

def is_meqpolclog(obj):
 if str(obj.__class__)=="<class 'Timba.dmi.MeqPolcLog'>":
  return True
 else:
  return False
def is_meqpolc(obj):
 if str(obj.__class__)=="<class 'Timba.dmi.MeqPolc'>":
  return True
 else:
  return False

def serialize_funklet(fnklt):
 #print fnklt
 coeff=fnklt['coeff'] # this is a numarray
 if coeff.size()>1:
  return coeff.tolist()
 else: # return scalar
  #print "coeff=",coeff
  #print "sum=",coeff.getreal()
  return coeff.getreal()
 # is we have a compiled funklet, we can return a dict
 # to be done
   
#########################################################################

#=====================================================================
#=====================================================================
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns)
