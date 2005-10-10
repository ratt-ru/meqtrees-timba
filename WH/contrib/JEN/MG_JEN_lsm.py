# MG_JEN_lsm.py

# Short description:
#   A script to explore the possibilities of the LSM

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 sep 2005: creation

# Copyright: The MeqTree Foundation

# Full description:


   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

# from numarray import *
# from string import *
# from copy import deepcopy
from random import *

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *
from Timba.Contrib.JEN import MG_JEN_Sixpack
from Timba.Contrib.SBY import MG_SBY_grow_tree

#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_lsm.py',
            last_changed='h29sep2005',
            trace=False)                       # If True, produce progress messages  

# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)

# NB: Using False here does not work, because it regards EVERYTHING
#        as an orphan, and deletes it.....!?
# Settings.orphans_are_roots = True





#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# The following non-standard setup (kludge) is make it possible
# to rebuild the forest after defining patches in the lsm. 

def _define_forest (ns):
   """Dummy function, just to define global nodescope my_ns"""
   global my_ns
   my_ns = ns
   # Create a single node to get the 'Jobs' button on the browser (!?) 
   root = ns.root << (my_ns << 0) + (my_ns << 1) 
   return True

#----------------------------------------------------------------
# This function is started from the browser 'jobs' button

def _tdl_job_define_forest (mqs, parent):
   """Kludge version of stanrard _define_forest()"""
   global my_ns
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (my_ns, MG)

   # Assume that the lsm object has been created separately,
   # e.g. via one of the _tdl_jobs below.
   global lsm

   # Obtain the list of the brightest punits
   plist = lsm.queryLSM(count=2)
   for punit in plist: 
      sp = punit.getSP()            # get_Sixpack()
      sp.display()
      if sp.ispoint():              # point source (Sixpack object)
	node = sp.iquv()
      else:	                    # patch (not a Sixpack object!)
        node = sp.root()
      cc.append(node)

   # Finished: 
   MG_JEN_exec.on_exit (my_ns, MG, cc)
   MG_SBY_grow_tree._update_forest(my_ns,mqs)
   return MG_JEN_exec.meqforest (mqs, parent)
   # return True









#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************



def lsm_343(ns):
   """Make a lsm from 3C343_nvss.txt"""
   
   # global lsm
   lsm = LSM()

   home_dir = os.environ['HOME']
   infile_name = home_dir + '/LOFAR/Timba/LSM/test/3C343_nvss.txt'
   infile=open(infile_name,'r')
   all=infile.readlines()
   infile.close()

   # regexp pattern
   pp=re.compile(r"""
      ^(?P<col1>\S+)  # column 1 'NVSS'
      \s*             # skip white space
      (?P<col2>[A-Za-z]\w+\+\w+)  # source name i.e. 'J163002+631308'
      \s*             # skip white space
      (?P<col3>\d+)   # RA angle - hr 
      \s*             # skip white space
      (?P<col4>\d+)   # RA angle - min 
      \s*             # skip white space
      (?P<col5>\d+(\.\d+)?)   # RA angle - sec
      \s*             # skip white space
      (?P<col6>\d+(\.\d+)?)   # eRA angle - sec
      \s*             # skip white space
      (?P<col7>\d+)   # Dec angle - hr 
      \s*             # skip white space
      (?P<col8>\d+)   # Dec angle - min 
      \s*             # skip white space
      (?P<col9>\d+(\.\d+)?)   # Dec angle - sec
      \s*             # skip white space
      (?P<col10>\d+(\.\d+)?)   # eDec angle - sec
      \s*             # skip white space
      (?P<col11>\d+)   # freq
      \s*             # skip white space
      (?P<col12>\d+(\.\d+)?)   # brightness - Flux
      \s*             # skip white space
      (?P<col13>\d*\.\d+)   # brightness - eFlux
      \s*
      \S+
      \s*$""",re.VERBOSE)
 
   linecount=0
   # read each source and insert to LSM
   for eachline in all:
      v=pp.search(eachline)
      if v!=None:
         linecount+=1
         print v.group('col2'), v.group('col12')
         s=Source(v.group('col2'))
         source_RA=float(v.group('col3'))+(float(v.group('col5'))/60.0+float(v.group('col4')))/60.0
         source_RA*=math.pi/12.0
         source_Dec=float(v.group('col7'))+(float(v.group('col9'))/60.0+float(v.group('col8')))/60.0
         source_Dec*=math.pi/180.0

         my_sixpack=MG_JEN_Sixpack.newstar_source(ns,name=s.name,
                                                  I0=eval(v.group('col12')),
                                                  SI=[random()],f0=1e6,
                                                  RA=source_RA,
                                                  Dec=source_Dec,
                                                  fsr_trace=False,
                                                  trace=False)
         # first compose the sixpack before giving it to the LSM
         SourceRoot=my_sixpack.sixpack(ns)
         # my_sixpack.display()
         print my_sixpack.label()
         lsm.add_source(s,brightness=eval(v.group('col12')),
                        sixpack=my_sixpack,
                        ra=source_RA, dec=source_Dec)

   # Finished:
   print "Inserted %d sources" % linecount 
   lsm.setNodeScope(ns)                       # remember node scope....(!)
   return lsm








#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    return MG_JEN_exec.meqforest (mqs, parent)


def _tdl_job_display (mqs, parent):
   global lsm
   # set the MQS proxy of LSM
   lsm.setMQS(mqs)
   cells = MG_JEN_exec.make_cells (domain='21cm',nfreq=10, ntime=5)
   lsm.setCells(cells)
   # query the MeqTrees using these cells
   lsm.updateCells()
   # display results
   lsm.display()


def _tdl_job_lsm_343 (mqs, parent):
   """Create an lsm for NVSS 3c343"""
   global lsm
   # ns = NodeScope()
   global my_ns
   lsm = lsm_343(my_ns)
   # MG_SBY_grow_tree._update_forest(my_ns,mqs)
   lsm.display()

def _tdl_job_lsm_query (mqs, parent):
   """Read the 3 brightest punits from the lsm"""
   global lsm
   plist = lsm.queryLSM(count=3)
   for pu in plist:
      my_sp = pu.getSP()
      my_sp.display()

def _tdl_job_dirdir (mqs, parent):
   """Show the contents(dir) of lsm and punit"""
   global lsm
   print '\n** dir(lsm):\n',dir(lsm)
   plist = lsm.queryLSM(count=1)
   print '\n** dir(punit):\n',dir(plist[0])


# Temporary: Create a default lsm:
lsm = LSM() 
# ns = NodeScope()
# lsm = lsm_343(ns)
# lsm.display()




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 1:
      lsm = lsm_343(ns)
      plist = lsm.queryLSM(count=3)
      for pu in plist:
         my_sp = pu.getSP()
         my_sp.display()

   if 0:
      MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
      # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




