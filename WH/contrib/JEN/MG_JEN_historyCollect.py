# MG_JEN_historyCollect.py

# Short description:
#   Functions related to MeqHistoryCollect nodes

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 03 oct 2005: tdl_jobs for different dimensions
# - 26 nov 2005: cleanup and simplification
# - 29 dec 2005: adapted to plots for all iterations
# - 22 mar 2006: adopted JEN_bookmarks.py

# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.JEN.util import JEN_bookmarks

from numarray import *

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_historyCollect.py',
                         last_changed='d26nov2005',
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

   # Make an input node to collect results from:
   freqtime = ns.freqtime << (ns << Meq.Freq) + (ns << Meq.Time)*(ns << Meq.Time)


   #---------------------------------------------------------------------------
   # Experiment 1: Just a hcoll
   # Any field from the result can be collected:
   input_index = 'VellSets/0/Value'                         # this is the default
   reqseq = insert_hcoll (ns, freqtime, input_index=input_index,
                          bookpage='insert_hcoll', bookfolder='hcoll')
   cc.append(reqseq)

   #---------------------------------------------------------------------------
   # Experiment 2: hcoll(s) for solver metrics and 'debug' values:
   if True:
      # Make a simple solver that tries to make parm equal to freqtime: 
      default = 0
      default = meq.polc(array([[0.0,0],[0,0]]))
      default = meq.polc(array([[0.0,0,0],[0,0,0]]))
      default = meq.polc(array([[0.0,0],[0,0],[0,0]]))
      default = meq.polc(array([[0.0,0,0],[0,0,0],[0,0,0]]))
      parm = ns.parm << Meq.Parm(default, node_groups='Parm')
      condeq = ns.condeq << Meq.Condeq(freqtime, parm)
      solver = ns.solver << Meq.Solver(condeq,
                                       solvable=parm,
                                       num_iter=10,
                                       # epsilon=1e-4,
                                       # last_update=True,
                                       # save_funklets=True,
                                       debug_level=10)
      # Make a bookmark for the solver plot:
      # JEN_bookmarks.bookmark (solver, udi='cache/result')
      JEN_bookmarks.bookmark (solver, viewer='Result Plotter')
      # JEN_bookmarks.bookmark (solver, udi='cache/result', viewer='Result Plotter')

      # Make a tensor node of hcoll nodes, and attach them to cc:
      cc.append(make_hcoll_solver_metrics (ns, solver, firstonly=True))


   #---------------------------------------------------------------------------
   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)







#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


def make_hcoll_solver_metrics (ns, solver, **pp):
   """Make a vector historyCollect nodes for solver metrics"""

   pp.setdefault('name', 'solver')      # Name of the solver
   pp.setdefault('bookfolder', 'solver_metrics')    # Name of the bookpage folder
   pp.setdefault('debug', True)         # if True, plot the debug record fields also
   pp.setdefault('firstonly', False)    # if True, plot the first iterations only
   
   # Make a qualifying integer to avoid node name clashes:
   uniqual = MG_JEN_forest_state.uniqual(MG.script_name+'::make_hcoll_solver_metrics()')
   hcoll_nodes = []

   # Make hcoll nodes for 'traditional' solver metrics:
   metrics = ['fit','rank','mu','stddev']

   pagename = 'hcoll_'+pp['name']+'_metrics'
   for metric in metrics:
      input_index = hiid('solver_result/metrics_array/0/'+metric)          
      hcoll_name = 'hcoll_'+pp['name']+'_m_'+metric
      hcoll = ns[hcoll_name](uniqual) << Meq.HistoryCollect(solver, verbose=True,
                                                            input_index=input_index,
                                                            top_label=hiid('history'))
      hcoll_nodes.append(hcoll)
      print 'creating bookmark for ',hcoll
      JEN_bookmarks.create(hcoll, viewer='History Plotter',
                           page=pagename, folder=pp['bookfolder'])

   if pp['firstonly']:
      # Optional: The value of the first [0] iteration only:
      pagename = 'hcoll_'+pp['name']+'_metrics0'
      for metric in metrics:
         input_index = hiid('solver_result/metrics/0/0/'+metric)          
         hcoll_name = 'hcoll_'+pp['name']+'_m0_'+metric
         hcoll = ns[hcoll_name](uniqual) << Meq.HistoryCollect(solver, verbose=True,
                                                               input_index=input_index,
                                                               top_label=hiid('history'))
         hcoll_nodes.append(hcoll)
         print 'creating bookmark for ',hcoll
         JEN_bookmarks.create(hcoll, viewer='History Plotter', 
                              page=pagename, folder=pp['bookfolder'])

   if pp['debug']: 
      # Optional: make hcoll nodes for 'debug' solver metrics:
      # debug = ['nonlin','seq','sol','prec','known','er','piv','neq']
      debug = ['nonlin','sol','prec','er']

      pagename = 'hcoll_'+pp['name']+'_debug'
      for metric in debug:
         input_index = hiid('solver_result/debug_array/0/'+metric)          
         hcoll_name = 'hcoll_'+pp['name']+'_db_'+metric
         hcoll = ns[hcoll_name](uniqual) << Meq.HistoryCollect(solver, verbose=True,
                                                               input_index=input_index,
                                                               top_label=hiid('history'))
         hcoll_nodes.append(hcoll)
         print 'creating bookmark for ',hcoll
         JEN_bookmarks.create(hcoll, viewer='History Plotter', 
                              page=pagename, folder=pp['bookfolder'])

      if pp['firstonly']:
         # Optional: The value of the first [0] iteration only:
         pagename = 'hcoll_'+pp['name']+'_debug0'
         for metric in debug:
            input_index = hiid('solver_result/debug/0/0/'+metric)          
            hcoll_name = 'hcoll_'+pp['name']+'_d0_'+metric
            hcoll = ns[hcoll_name](uniqual) << Meq.HistoryCollect(solver, verbose=True,
                                                                  input_index=input_index,
                                                                  top_label=hiid('history'))
            hcoll_nodes.append(hcoll)
            print 'creating bookmark for ',hcoll
            JEN_bookmarks.create(hcoll, viewer='History Plotter', 
                                 page=pagename, folder=pp['bookfolder'])

   # Return a tensor node of historyCollect nodes:
   root = ns.hcolls_solver_metrics(uniqual) << Meq.Composer(children=hcoll_nodes)
   return root



#------------------------------------------------------------------------------
# Insert hcoll node to collect history information from the given result field
# from the given node.

def insert_hcoll(ns, node, **pp):
   """Make (and insert) a historyCollect node for the (given field of the) given node"""

   pp.setdefault('input_index', 'VellSets/0/Value')   
   pp.setdefault('strip', True)                      # if True, strip off perturbed vells   
   pp.setdefault('mean', False)                      # if True, take the mean first   
   pp.setdefault('bookpage', None)                   # if string, make a bookmark
   pp.setdefault('bookfolder', None)                 # if string, make a bookfolder
   pp.setdefault('graft', True)                      # if True, insert a ReqSeq for requests

   # Make a qualifying integer to avoid node name clashes:
   uniqual = MG_JEN_forest_state.uniqual(MG.script_name+'::insert_hcoll()')

   # Perform some (optional) operations on the hcoll_input node
   hcoll_input = node
   if pp['strip']:
      hcoll_input = ns.stripper_hcoll(uniqual) << Meq.Stripper(hcoll_input)
   if pp['mean']:
      hcoll_input = ns.mean_hcoll(uniqual) << Meq.Mean(hcoll_input)

   # Deal with the target field of the result record:
   if isinstance(pp['input_index'], str):
      pp['input_index'] = hiid(pp['input_index'])

   # Make the historyCollect node itself:
   if isinstance(node, str):                       # node given as (string) node name
      name = 'hcoll_'+node
   else:                                           # assume node given as nodestub
      name = 'hcoll_'+node.name             
   hcoll = ns[name](uniqual) << Meq.HistoryCollect(hcoll_input, verbose=True,
                                                   input_index=pp['input_index'],
                                                   top_label=hiid('history'))
   # Make a bookmark for the hcoll, if required:
   if pp['bookpage'] or pp['bookfolder']:
      JEN_bookmarks.create(hcoll, viewer='History Plotter',
                           page=pp['bookpage'], folder=pp['bookfolder'])

   # Optionally, make a reqseq node to issue requests to hcoll,
   # while passing on the result of the original node
   output = hcoll
   if pp['graft']:
      output = ns.reqseq_hcoll(uniqual) << Meq.ReqSeq (children=[hcoll,node], result_index=1)
   return output


#------------------------------------------------------------------------------
# Special version of insert_hcoll() for collecting flags:

def insert_hcoll_flags (ns, node, **pp):
   """Special version of .insert_hcoll() for collecting flags"""
   pp.setdefault('input_index', 'VellSets/0/Flags')
   pp['input_index'] = 'VellSets/0/Flags'
   return insert_hcoll (ns, node, **pp)



#------------------------------------------------------------------------------
# Remarks:
#------------------------------------------------------------------------------

# -) The input_index allows the specification of the field from which info is to
#    be collected. Its syntax is still a bit primitive:
#    - What if the result has more 'planes' than one (0), but I do not know in
#      advance how many?
#    - The solver metrics produce a record with fit,rank,mu etc for each iteration.
#      There does not seem to be a way to extract the vector of all mu-values for
#      all iterations (the nr of which may vary from snippet to snippet!)
#      So we need some kind of transpose of the metrics result, and AGW should be
#      able to absorb sequences of vectors of different length...!

# -) For flags, the first result in the history sequence is not plotted correctly.
#    It does not show any flags, while it does have them (use record browser)


# -) The next step is to pull out data and flags, and concatenate
#         with a dataCollect for AGW to handle....     



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
                          increment=True,
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
                             increment=True,
                             save=False, trace=False) 
   MG_JEN_forest_state.save_meqforest(mqs) 
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
                             increment=True,
                             save=False, trace=False)
   MG_JEN_forest_state.save_meqforest(mqs) 
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
                             increment=True,
                             save=False, trace=False)
   MG_JEN_forest_state.save_meqforest(mqs)  
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
                             increment=True,
                             save=False, trace=False)
   MG_JEN_forest_state.save_meqforest(mqs)  
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




