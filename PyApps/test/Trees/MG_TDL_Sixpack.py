script_name = 'MG_TDL_Sixpack.py'

# Short description:
# Illustrates the use of Sixpack Objects 


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


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

############ globals
# global Sixpack
my_sp=None

def _define_forest (ns):
  global my_sp
  my_name='my_sixpack'
  # create some node stubs for the sixpack
  # first some parameters
  ns.f<<Meq.Parm(meq.polclog([1,0.1,0.01]))
  ns.t<<Meq.Parm(meq.polclog([0.01,0.1,1]))
  # next the node stubs
  stubI=ns['Istub']<<1.1*Meq.Sin(ns.f+ns.t)
  stubQ=ns['Qstub']<<2.0*Meq.Cos(ns.f)
  stubU=ns['Ustub']<<2.1*Meq.Sin(ns.f-2)
  stubV=ns['Vstub']<<2.1*Meq.Cos(ns.f-2)
  stubRA=ns['RAstub']<<2.1*Meq.Cos(ns.f-2)*Meq.Sin(ns.t)
  stubDec=ns['Decstub']<<2.1*Meq.Cos(ns.f-2)*Meq.Sin(ns.t)

  # now create the sixpack
  my_sp=TDL_Sixpack.Sixpack(label=my_name,\
   nodescope=ns, RA=stubRA,Dec=stubDec,sI=stubI,\
   sQ=stubQ,sU=stubU,sV=stubV)
  my_sp.display()

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
   # create cells
   f0 = 1200e6
   f1 = 1600e6
   t0 = 0.0
   t1 = 1.0
   nfreq = 3
   ntime = 2
   freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
   my_cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
   my_sp.display()
   # send to kernel
   request = meq.request(my_cells,eval_mode=1);
   mqs.meq('Node.Execute',record(name=my_sp.label(),request=request));




#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',script_name,':\n'

   ns = NodeScope()                # if used: from Timba.TDL import *
   _define_forest(ns)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************
