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

   global lsm

   # obtain the punit list of the 3 brightest ones
   plist = lsm.queryLSM(count=3)
   for pu in plist:
      my_sp = pu.getSP()
      my_sp.display()

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)









#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************



def lsm_343(ns):
   """Make a lsm from 3C343_nvss.txt"""
   
   global lsm
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
   lsm.setNodeScope(ns)                       # remember node scope....(?)
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
   ns = NodeScope()
   lsm = lsm_343(ns)
   lsm.display()

def _tdl_job_lsm_query (mqs, parent):
   """Read the 3 brightest punits from the lsm"""
   global lsm
   plist = lsm.queryLSM(count=3)
   for pu in plist:
      my_sp = pu.getSP()
      my_sp.display()


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




