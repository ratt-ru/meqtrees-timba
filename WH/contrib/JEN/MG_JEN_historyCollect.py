# MG_JEN_historyCollect.py

# Short description:
#   Functions related to MeqHistoryCollect nodes

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 03 oct 2005: tdl_jobs for different dimensions

# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *

from numarray import *

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_historyCollect.py',
                         last_changed='h02oct2005',
                         nfreq=5,                    # used in requests
                         ntime=8,                   # used in requests
                         trace=False)             # If True, produce progress messages  


# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)




#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   node = ns.freqtime << (ns << Meq.Freq) + (ns << Meq.Time)*(ns << Meq.Time)
   input = node

   node = ns.stripper << Meq.Stripper(node)
   # node = ns.mean << Meq.Mean(node)

   # Any field from the result can be collected, default is: 
   input_index = hiid('VellSets/0/Value')          
   node = ns.hcoll << Meq.HistoryCollect(node, verbose=True,
                                         input_index=input_index,
                                         top_label=hiid('visu'))

   MG_JEN_forest_state.bookmark(node, viewer='History Plotter', page='hcoll')
   MG_JEN_forest_state.bookmark(node, viewer='Record Browser', page='hcoll')

   attrib = record(plot=record(), tag='tag')
   attrib['plot'] = record(type='spectra', title=MG.script_name,
                           spectrum_color='hippo',
                           x_axis='#', y_axis='hcoll')
   sc = []
   top_label = hiid('visu')
   sc.append(ns.dcoll_stripper << Meq.DataCollect(ns.stripper, attrib=attrib, top_label=top_label))
   # sc.append(ns.dcoll_mean << Meq.DataCollect(ns.mean, attrib=attrib, top_label=top_label))
   sc.append(ns.dcoll_hcoll << Meq.DataCollect(ns.hcoll, attrib=attrib, top_label=top_label))
   cc.append(ns.root << Meq.Add(input,stepchildren=sc))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)







#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************






#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

x = 0

def _test_forest (mqs, parent):
   """One request at a time"""
   global x
   x += 1
   MG_JEN_exec.meqforest (mqs, parent, nfreq=MG['nfreq'], ntime=MG['ntime'],
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             save=True, trace=False) 
   return True

#--------------------------------------------------------
# Sequences for requests with different freq/time dimensions:

def _tdl_job_2D_freqtime (mqs, parent):
   """Execute the forest for a sequence of (2D) requests"""
   global x
   x -= 1.5
   for i in range(10):
      x += 1
      MG_JEN_exec.meqforest (mqs, parent, nfreq=MG['nfreq'], ntime=MG['ntime'],
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             save=False, trace=False) 
   MG_JEN_exec.save_meqforest(mqs) 
   return True

#--------------------------------------------------------
def _tdl_job_1D_freq (mqs, parent):
   """Execute the forest for a sequence of (1D) requests"""
   global x
   x -= 1.5
   for i in range(10):
      x += 1
      MG_JEN_exec.meqforest (mqs, parent, nfreq=MG['nfreq'], ntime=1,
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             save=False, trace=False) 
   return True

#--------------------------------------------------------
def _tdl_job_1D_time (mqs, parent):
   """Execute the forest for a sequence of (1D) requests"""
   global x
   x -= 1.5
   for i in range(10):
      x += 1
      MG_JEN_exec.meqforest (mqs, parent, nfreq=1, ntime=MG['ntime'],
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             save=False, trace=False) 
   return True

#--------------------------------------------------------
def _tdl_job_scalar (mqs, parent):
   """Execute the forest for a sequence of (scalar) requests"""
   global x
   x -= 1.5
   for i in range(10):
      x += 1
      MG_JEN_exec.meqforest (mqs, parent, nfreq=1, ntime=1,
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             save=False, trace=False) 
   return True



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   if 1:
      MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=10)

   ns = NodeScope()                # if used: from Timba.TDL import *


   if 1:
       MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
       # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




