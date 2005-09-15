script_name = 'MG_JEN_historyCollect.py'
last_changed = 'h10sep2005'

# Short description:
#   Functions related to MeqHistoryCollect nodes

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 


#================================================================================
# Import of Python modules:

from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed


from Timba.TDL import *
# Possibly better, namespace-wise?
#   from Timba import TDL
#   from Timba.TDL import dmi_type, Meq, record, hiid

from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_math
# from Timba.Contrib.JEN import MG_JEN_funklet




#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
   # Perform some common initial actions, and return empty list cc:
   cc = MG_JEN_exec.on_entry (ns, script_name)

   node = ns.freqtime << (ns.freq << Meq.Freq) + (ns.time << Meq.Time)
   input = node

   node = ns.stripper << Meq.Stripper(node)
   node = ns.mean << Meq.Mean(node)
   node = ns.hcoll << Meq.HistoryCollect(node, verbose=True,top_label=hiid('visu'))

   attrib = record(plot=record(), tag='tag')
   attrib['plot'] = record(type='spectra', title=script_name,
                           spectrum_color='hippo',
                           x_axis='#', y_axis='hcoll')
   sc = []
   sc.append(ns.dcoll_stripper << Meq.DataCollect(ns.stripper, attrib=attrib, top_label=hiid('visu')))
   sc.append(ns.dcoll_mean << Meq.DataCollect(ns.mean, attrib=attrib, top_label=hiid('visu')))
   sc.append(ns.dcoll_hcoll << Meq.DataCollect(ns.hcoll, attrib=attrib, top_label=hiid('visu')))
   cc.append(ns.root << Meq.Add(input,stepchildren=sc))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)






#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================




#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)



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
   print '\n*******************\n** Local test of:',script_name,':\n'

   # Generic test:
   MG_JEN_exec.without_meqserver(script_name, callback=_define_forest, recurse=10)

   # Various specific tests:
   # ns = TDL.NodeScope()          # if used: from Timba import TDL
   ns = NodeScope()                # if used: from Timba.TDL import *

   if 1:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




