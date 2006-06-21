
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

script_name = 'MG_SBY_grow_tree.py'

# Short description:
# shows how to dynamically grow a tree upon user input

# Author: Sarod Yatawatta (SBY), Dwingeloo

# History:
# - 26 aug 2005: creation

# Copyright: The MeqTree Foundation 

# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq


#############################
### Some global variables needed
#### Node Scope
my_ns=None;
#### Root of the tree
my_root=None;
##### a counter user to generate unique names
my_counter=0;
##### global MQS object
my_mqs=None;

#=====================================================================
#=====================================================================
def _define_forest (ns):
   global my_ns,my_root,my_counter;

   # remember this nodescope
   my_ns=ns;
   # create one MeqParm Node,
   # automatically this becomes the only root node
   my_root=my_ns['Node#'+str(my_counter)]<<Meq.Parm(0);

   # Increment count
   my_counter+=1;



#=====================================================================
#=====================================================================
################################
### Test forest,
#### Each time you run this, your tree will grow by one node
def _test_forest (mqs, parent):
   global my_ns,my_root,my_counter,my_mqs;

   # remember the MQS object
   my_mqs=mqs;
   # create a new MeqAdd node and make it the root of the existing 
   # subtree
   my_new_root=my_ns['Node#'+str(my_counter)]<<Meq.Add(children='Node#'+str(my_counter-1));
   my_root=my_new_root;
   my_counter+=1;

   # send the new tree to the kernel
   my_ns.Resolve();
   # kernel will recreate the forest
   mqs.meq('Clear.Forest');
   mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),my_ns.AllNodes().itervalues())));
   mqs.meq('Resolve.Batch',record(name=list(my_ns.RootNodes().iterkeys())))
   fst = getattr(Timba.TDL.Settings,'forest_state',record());
   mqs.meq('Set.Forest.State',record(state=fst));


###################################################################
####### Illustrates the use of importable function _update_forest()
def _tdl_job_dynamic_update(mqs,parent):
  # note we do not use the default argumets given
  global my_ns, my_mqs
  global my_counter,my_root
  # do somthing with the current forest
  my_new_root=my_ns['Node#'+str(my_counter)]<<Meq.Add(children='Node#'+str(my_counter-1));
  my_root=my_new_root;
  my_counter+=1;

  # call the importable function 
  _update_forest(my_ns,my_mqs)


#########################################################################
###### importable function
def _update_forest(ns,mqs):
   """Dynamically grow trees. Needs mqs and nodescope
     objects"""
   # send the new tree to the kernel
   ns.Resolve();
   # kernel will recreate the forest
   mqs.meq('Clear.Forest');
   mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),ns.AllNodes().itervalues())));
   mqs.meq('Resolve.Batch',record(name=list(ns.RootNodes().iterkeys())))
   fst = getattr(Timba.TDL.Settings,'forest_state',record());
   mqs.meq('Set.Forest.State',record(state=fst));

 
#=====================================================================
#=====================================================================
if __name__ == '__main__':
  pass
