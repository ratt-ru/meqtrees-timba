# MG_JEN_lsm.py

# Short description:
#   A script to explore the possibilities of the LSM

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 sep 2005: creation
# - 11 feb 2006: total overhaul

# Copyright: The MeqTree Foundation

# Full description:


   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from Timba.Trees import JEN_inarg
from Timba.Trees import JEN_inargGui

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
# from Timba.Contrib.SBY import MG_SBY_grow_tree






#********************************************************************************
#********************************************************************************
#******************** PART II: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************



def lsm_343(ns):
   """Make a lsm from 3C343_nvss.txt"""
   
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

         my_sixpack=MG_JEN_Sixpack.newstar_source(ns, punit=s.name,
                                                  I0=eval(v.group('col12')),
                                                  SI=[random()],f0=1e6,
                                                  RA=source_RA,
                                                  Dec=source_Dec,
                                                  fsr_trace=False,
                                                  trace=False)
         # first compose the sixpack before giving it to the LSM
         SourceRoot=my_sixpack.sixpack(ns)
         # my_sixpack.display()
         # print my_sixpack.label()
         lsm.add_source(s,brightness=eval(v.group('col12')),
                        sixpack=my_sixpack,
                        ra=source_RA, dec=source_Dec)

   # Finished:
   print "Inserted %d sources" % linecount 
   lsm.setNodeScope(ns)                       # remember node scope....(!)
   lsm.save('3c343.lsm')
   # lsm.save(MG['lsm_current'])                        # 
   return lsm

#--------------------------------------------------------------------------------

def make_single (ns=None, lsm=None, cc=[], radec=[], **inarg):
   """Define a single test-source"""

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_lsm::make_single()', version='10feb2006',
                           description=make_single.__doc__)
   JEN_inarg.nest(pp, MG_JEN_Sixpack.newstar_source(_getdefaults=True))
 
   if False:
      # Source positions may be supplied as nodes:
      JEN_inarg.define(pp, 'RA0', None, choice=[], hide=True,  
                       help='If RA0 is a node, RA0+dRA overrides RA')
      JEN_inarg.define(pp, 'Dec0', None, choice=[], hide=True,   
                       help='If Dec0 is a node, Dec0+dDec overrides Dec')
      JEN_inarg.define(pp, 'dRA', 0.0, choice=[], hide=True,   
                       help='RA offset (arcsec): RA = RA0 + dRA')
      JEN_inarg.define(pp, 'dDec', 0.0, choice=[], hide=True,   
                       help='Dec offset (arcsec): Dec = Dec0 + dDec')

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   print 'funcname =',funcname

   # Create the source defined by pp:
   sp = MG_JEN_Sixpack.newstar_source(ns, _inarg=pp)
   sp.display()
   cc.append(MG_JEN_Sixpack.make_bookmark(ns, sp))
   MG_JEN_Sixpack.collect_radec(radec, sp)

   # Compose the sixpack before adding it to the lsm:
   sp.sixpack(ns)
   sp.display()
   lsm.add_sixpack(sixpack=sp)
   return sp


#--------------------------------------------------------------------------------

def make_grid (ns=None, lsm=None, cc=[], radec=[], **inarg):
   """Define a rectangular grid of test-sources"""

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_lsm::make_grid()', version='10feb2006',
                           description=make_single.__doc__)
   JEN_inarg.nest(pp, MG_JEN_Sixpack.newstar_source(_getdefaults=True))
 
   # Source positions may be supplied as nodes:
   JEN_inarg.define(pp, 'nRA2', 1, choice=[0,1,2,3],   
                    help='(half) nr of sources in RA direction')
   JEN_inarg.define(pp, 'nDEC2', 1, choice=[0,1,2,3],   
                    help='(half) nr of sources in DEC direction')
   JEN_inarg.define(pp, 'gRA', 10, choice=[],    
                    help='RA grid spacing (arcsec)')
   JEN_inarg.define(pp, 'gDEC', 10, choice=[],    
                    help='DEC grid spacing (arcsec)')

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   print 'funcname =',funcname

   # Create the source defined by pp:
   sp = MG_JEN_Sixpack.newstar_source(ns, _inarg=pp)
   sp.display()
   cc.append(MG_JEN_Sixpack.make_bookmark(ns, sp))
   MG_JEN_Sixpack.collect_radec(radec, sp)

   # Compose the sixpack before adding it to the lsm:
   sp.sixpack(ns)
   sp.display()
   lsm.add_sixpack(sixpack=sp)
   return sp


#--------------------------------------------------------------------------------

def make_spiral (ns=None, lsm=None, cc=[], radec=[], **pp):
   """Define a spiral pattern of test-sources"""
   return True



#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

def description ():
    """MG_JEN_lsm.py is used to create Local Sky Models (LSM) by hand"""
    return True

#-------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_lsm', description=description.__doc__)
JEN_inarg.define (MG, 'last_changed', 'd30jan2006', editable=False)

JEN_inarg.define (MG, 'LSM', 'lsm_current.lsm', browse='*.lsm',
                  help='(file)name of the Local Sky Model')

JEN_inarg.define (MG, 'test_pattern', None,
                  choice=[None,'single','grid','spiral'],
                  help='pattern of test-sources to be generated')

JEN_inarg.nest(MG, make_single(_getdefaults=True))
# JEN_inarg.nest(MG, make_grid(_getdefaults=True))
# JEN_inarg.nest(MG, make_spiral(_getdefaults=True))

JEN_inarg.define (MG, 'count', 2, choice=[1,2,3,5,10,100,1000],
                  help='nr of LSM sources to be used')

# inarg = MG_JEN_Sixpack.newstar_source(_getdefaults=True) 
# JEN_inarg.attach(MG, inarg)




#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)

# NB: Using False here does not work, because it regards EVERYTHING
#        as an orphan, and deletes it.....!?
# Settings.orphans_are_roots = True


# Create an empty global lsm, just in case:
lsm = LSM()



#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _tdl_predefine (mqs, parent, **kwargs):
   res = True
   if parent:
      QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
      try:
         igui = JEN_inargGui.ArgBrowser(parent)
         igui.input(MG, set_open=False)
         res = igui.exec_loop()
         if res is None:
            raise RuntimeError("Cancelled by user");
      finally:
         QApplication.restoreOverrideCursor()
   return res




#**************************************************************************

def _define_forest (ns, **kwargs):

   # The MG may be passed in from _tdl_predefine():
   # In that case, override the global MG record.
   global MG
   if len(kwargs)>1: MG = kwargs
   
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)
   radec = []                          # for collect_radec()


   # Load the specified lsm into the global lsm object:
   global lsm
   # lsm = LSM()
   lsm.load(MG['LSM'],ns)


   # Make a pattern of one or more test-sources, if required:
   if isinstance(MG['test_pattern'], str):
      if MG['test_pattern']=='single':
         make_single(ns, lsm=lsm, cc=cc, radec=radec, **MG)
      elif MG['test_pattern']=='grid':
         make_grid(ns, lsm=lsm, cc=cc, radec=radec, **MG)
      elif MG['test_pattern']=='spiral':
         make_spiral(ns, lsm=lsm, cc=cc, radec=radec, **MG)
      else:
         print 'test_pattern not recognised:',MG['test_pattern']

   lsm.display()


   if False:
      # Obtain the Sixpacks of the brightest punits.
      # Turn the point-sources in Cohsets with DFT KJonesets
      plist = lsm.queryLSM(count=MG['count'])
      print '\n** plist =',type(plist),len(plist)
      for punit in plist: 
         sp = punit.getSP()              # get_Sixpack()
         cc.append(MG_JEN_Sixpack.make_bookmark(ns, sp))
         MG_JEN_Sixpack.collect_radec(radec, sp)
         # qual = str(sp.label())
         # sp.display()
         if sp.ispoint():                # point source (Sixpack object)
            pass
         else:	                        # patch (not a Sixpack object!)
            node = sp.root()            # ONLY valid for a patch...#
            cc.append(node)             # ....?

   # Make a radec root node (tidier)
   MG_JEN_Sixpack.collect_radec(radec, ns=ns)
   
   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    return MG_JEN_exec.meqforest (mqs, parent)
    # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm',nfreq=10, ntime=5)


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





#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG['script_name'],':\n'

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 1:
      igui = JEN_inargGui.ArgBrowser()
      igui.input(MG, set_open=False)
      igui.launch()
       

   if 0:
      lsm = lsm_343(ns)
      plist = lsm.queryLSM(count=3)
      for pu in plist:
         my_sp = pu.getSP()
         my_sp.display()

   if 0:
      MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
      # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
   print '\n** End of local test of:',MG['script_name'],'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




