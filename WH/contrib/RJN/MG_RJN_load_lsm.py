script_name = 'MG_RJN_load_lsm.py'

# Short description:
#   First try at generating a LSM and connecting Point and Patch P-Units

# Keywords: LSM


# History:
# - 12 Sep 2005: creation
# - 26 Oct 2005: adaptation from /SBY/MG_LSM_test.py

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba import utils
_dbg = utils.verbosity(0, name='LSM_load')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed


from Timba.TDL import *
from Timba.TDL import Settings
from Timba.Meq import meq
from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *

from Timba.Contrib.RJN import RJN_sixpack_343

from random import *
# to force caching put 100
Settings.forest_state.cache_policy = 100


# Create Empty LSM - global
lsm=LSM()
#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
 global lsm
 
 # Load a predefined LSM
 lsm.load('3c343_c.lsm',ns);

 # Get all Cat. 1 P-Units
 plist = lsm.queryLSM(cat=1);

 print lsm.getPUnits()
 print len(plist)

 child_list = [];

 for punit in plist:
   if (punit._patch_name == None):
     print 'Gotcha!', punit.name
     if (punit.type == 0) :
       print 'Point', punit.name, punit.type
       sixpack_name = 'sixpack:q='+punit.name
       child_list.append(sixpack_name)
     else:
       print 'Patch', punit.name, punit.type
       sixpack_name = 'sixpack:q='+punit.name
       child_list.append(sixpack_name)

 predict_root = ns['predict']<<Meq.Add(children=child_list);

########################################################################





#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================





#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
 global lsm
 #display LSM within MeqBrowser
 #l.display()
 # set the MQS proxy of LSM
 lsm.setMQS(mqs)

 

 f0 = 1200e6
 f1 = 1600e6
 t0 = 0.0
 t1 = 1.0
 nfreq = 1
 ntime = 1
 # create cells
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 # set the cells to LSM
 lsm.setCells(cells)
 # query the MeqTrees using these cells
 lsm.updateCells()
 # display results
 #lsm.display()

 request = meq.request(cells=cells, eval_mode=0);
 args = record(name='predict', request=request);
 mqs.meq('Node.Execute', args, wait=False);

##############################################################
#### test routine to query the LSM and get some Sixpacks from   
#### PUnits
def _tdl_job_query_punits(mqs, parent):
 global lsm
 # obtain the punit list of the 3 brightest ones
 plist=lsm.queryLSM(count=3)
 for pu in plist:
  my_sp=pu.getSP()
  my_sp.display()

#####################################################################
#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
  print '\n*******************\n** Local test of:',script_name,':\n'
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  #display LSM without MeqBrowser
  # create cell
  freqtime_domain = meq.domain(10,1000,0,1);
  cells =meq.cells(domain=freqtime_domain, num_freq=2,  num_time=3);
  lsm.setCells(cells)
  lsm.display(app='create')
#********************************************************************************
#********************************************************************************




