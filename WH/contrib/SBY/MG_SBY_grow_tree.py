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

#=====================================================================
#=====================================================================
def _define_forest (ns):
   global my_ns,my_root,my_counter;

   # remembet this nodescope
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
   global my_ns,my_root,my_counter;

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


#=====================================================================
#=====================================================================
if __name__ == '__main__':
  pass
