script_name = 'MG_TDL_Sixpack.py'

# Short description:
# Illustrates the use of Sixpack Objects 

# Keywords: ....

# Author: Sarod Yatawatta (SBY), Dwingeloo

# History:
# - 8 Sep 2005: creation

# Copyright: The MeqTree Foundation 

# Import of Python modules:

from Timba import utils
_dbg = utils.verbosity(0, name='Sixpack')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dTDL_Sixpack=3
# level 0 is always printed


from Timba.TDL import *
from Timba.Meq import meq

#from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Trees import TDL_Sixpack


from Timba.Contrib.JEN import MG_JEN_sixpack
#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

############ globals
# global Sixpack
my_sp=None

def _define_forest (ns):
  global my_sp
  my_name='unique_name'
  # use JEN code to generate custom subtrees for this sixpack
  sixpack_stubs=MG_JEN_sixpack.newstar_source(ns, name=my_name,I0=10, SI=[0.1],f0=1e6,RA=0.0, Dec=0.0,trace=0)
 
  iquv=sixpack_stubs['iquv']
  radec=sixpack_stubs['radec']
  my_sp=TDL_Sixpack.Sixpack(name=my_name,label='my first sixpack',\
   ns=ns, RA=radec['RA'],Dec=radec['Dec'],StokesI=iquv['StokesI'],\
   StokesQ=iquv['StokesQ'],StokesU=iquv['StokesU'],StokesV=iquv['StokesV'])
  my_sp.display()
  # the following should fail because we have not connected to a server
  my_sp.getVellsDimension('I',0,0)
  my_sp.getVellsValue('I',0,0)

  # resolve the forest
  ns.Resolve()


#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================

#-------------------------------------------------------------------------------
# Example:


#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************



#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   global my_sp
   # set the meqserver proxy
   my_sp.setMQS(mqs)

   
   # create cells
   f0 = 1200e6
   f1 = 1600e6
   t0 = 0.0
   t1 = 1.0
   nfreq = 3
   ntime = 2
   freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
   my_cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
   # set the cells 
   my_sp.setCells(my_cells)
   # query the MeqTrees using these cells
   my_sp.updateVells()
   # get some values
   # 'I','Q','U','V' can be given
   print my_sp.getVellsDimension('I',0,0)
   print my_sp.getVellsValue('I',0,0)

   my_sp.display()



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',script_name,':\n'

   ns = NodeScope()                # if used: from Timba.TDL import *
   _define_forest(ns)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************
