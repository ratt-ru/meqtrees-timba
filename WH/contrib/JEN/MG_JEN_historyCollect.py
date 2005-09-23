# MG_JEN_historyCollect.py

# Short description:
#   Functions related to MeqHistoryCollect nodes

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *

MG = record(script_name='MG_JEN_historyCollect.py', last_changed = 'h22sep2005')

from numarray import *

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG.script_name)




#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   node = ns.freqtime << (ns.freq << Meq.Freq) + (ns.time << Meq.Time)
   input = node

   node = ns.stripper << Meq.Stripper(node)
   node = ns.mean << Meq.Mean(node)
   node = ns.hcoll << Meq.HistoryCollect(node, verbose=True,top_label=hiid('visu'))

   attrib = record(plot=record(), tag='tag')
   attrib['plot'] = record(type='spectra', title=MG.script_name,
                           spectrum_color='hippo',
                           x_axis='#', y_axis='hcoll')
   sc = []
   sc.append(ns.dcoll_stripper << Meq.DataCollect(ns.stripper, attrib=attrib, top_label=hiid('visu')))
   sc.append(ns.dcoll_mean << Meq.DataCollect(ns.mean, attrib=attrib, top_label=hiid('visu')))
   sc.append(ns.dcoll_hcoll << Meq.DataCollect(ns.hcoll, attrib=attrib, top_label=hiid('visu')))
   cc.append(ns.root << Meq.Add(input,stepchildren=sc))


   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)


# NB: See MG_JEN_exec.py to see which services its functions provide
# exactly.  In general, _define_forest() should define a number of
# carefully designed 'experiments' in the form of subtrees. Their root
# nodes are appended to the list cc. Groups of experiments may be
# bundled The function .on_ext() ties the nodes in cc together by
# making them the children of a single root node, with the specified
# name (default is MG.script_name). The latter is executed by the
# function _test_forest() and its _tdl_job_ relatives (see below).

# Groups of experiments may be bundled with the .bundle() function in
# exactly the same way (indeed, .on_exit() uses .bundle()). The bundle
# names, which should be unique, are used to generate bookmarks for the
# inspection of the bundle results. This is highly convenient.








#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************






#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************



#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

# The function MG_JEN_exec.meqforest() can be used in various ways:
# If not explicitly supplied, a default request will be used:
#    return MG_JEN_exec.meqforest (mqs, parent)
# It is also possible to give an explicit request, cells or domain
# In addition, qualifying keywords will be used when sensible
# The following call shows the default settings explicity:
#    return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False) 
# There are some predefined domains:
#    return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')   # (100-110 MHz)
#    return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')    # (1350-1420 MHz)


def _test_forest (mqs, parent):

   if False:
      # Execute once, with a default request:
      return MG_JEN_exec.meqforest (mqs, parent)

   else:
      # Alternative: Execute the forest for a sequence of requests:
      for x in range(10):
         MG_JEN_exec.meqforest (mqs, parent, nfreq=4, ntime=5,
                                f1=x, f2=x+1, t1=x, t2=x+1,
                                save=False, trace=False) 
      MG_JEN_exec.save_meqforest(mqs) 
      return True



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   if 1:
      MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=10)

   # Various specific tests:
   # ns = TDL.NodeScope()          # if used: from Timba import TDL
   ns = NodeScope()                # if used: from Timba.TDL import *

   if 0:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', MG.script_name)
      # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)

   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




