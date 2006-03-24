# MG_JEN_lsm.py

# Short description:
#   A script to explore the possibilities of the LSM

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 sep 2005: creation
# - 11 feb 2006: total overhaul
# - 22 mar 2006: standard lsm generation

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

from numarray import *
# from string import *
# from copy import deepcopy
from random import *

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *
from Timba.Contrib.JEN import MG_JEN_Sixpack






#********************************************************************************
#********************************************************************************
#******************** PART II: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************



def nvss_3c343(ns, trace=True):
   """Make a lsm for 3C343 from an nvss txt-file"""
   nvss2lsm (ns, nvss_file='/LOFAR/Timba/LSM/test/3C343_nvss.txt', trace=trace)
   return True

#-----------------------------------------------------------------------------
   
def nvss_Abell963(ns, trace=True):
   """Make lsm(s) for Abell963 from nvss txt-file"""
   nvss2lsm (ns, nvss_file='/LOFAR/Timba/LSM/test/abel963.txt', trace=trace)
   if False:
      # Empty
      nvss2lsm (ns, nvss_file='/LOFAR/Timba/LSM/test/Abell963catb.txt', trace=trace)
   return True

#-----------------------------------------------------------------------------
   
def nvss_all(ns, trace=True):
   """Regenerate lsm(s) for all available nvss txt-files"""
   nvss_3c343(ns, trace=trace)
   nvss_Abell963(ns, trace=trace)
   return True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

def nvss2lsm(ns, nvss_file=None, lsm_name=None, trace=True):
   """Make a lsm from the given nvss (txt) file"""

   if trace:
      print '\n**************************************************************'
      print '** nvss2lsm(',lsm_name,') <- nvss =',nvss_file
      print '**************************************************************\n'

   if not isinstance(nvss_file, str):
      print '** ERROR **: nvss_file =',nvss_file
      return False

   # Make the lsm (file) name from the input nvss_file:
   if not isinstance(lsm_name, str):
      ss = nvss_file.split('/')
      lsm_name = ss[len(ss)-1]                       # remove the directories
      lsm_name = lsm_name.split('.')[0]              # remove the file extension (.txt)
      lsm_name += '.lsm'                             # append .lsm extension
      
   # Use the global lsm.
   global lsm
   lsm = LSM()                                       # make a new one

   #---------------------------------------------------------------------------
   # Alternative:
   if True:
      home_dir = os.environ['HOME']
      infile_name = home_dir + nvss_file
      lsm.build_from_catalog(infile_name, ns)
      if trace:
         print '** Finished build_from_catalog()' 
      lsm.save('lsm_current.lsm')                        # 
      lsm.save(lsm_name)
      lsm.display()
      if trace:
         print '** Saved as:',lsm_name,'   (and lsm_current.lsm)'
         print '**************************************************************\n'
      return True
   #---------------------------------------------------------------------------

   # Read the nvss text-file:
   home_dir = os.environ['HOME']
   infile_name = home_dir + nvss_file
   infile = open(infile_name, 'r')
   all = infile.readlines()
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
 
   # read each source and insert to LSM
   linecount=0
   for eachline in all:
      v = pp.search(eachline)
      if v!=None:
         linecount+=1
         if trace:
            print linecount,':',v.group('col2'), v.group('col12')
         s=Source(v.group('col2'))
         source_RA=float(v.group('col3'))+(float(v.group('col5'))/60.0+float(v.group('col4')))/60.0
         source_RA*=math.pi/12.0
         source_Dec=float(v.group('col7'))+(float(v.group('col9'))/60.0+float(v.group('col8')))/60.0
         source_Dec*=math.pi/180.0

         my_sixpack = MG_JEN_Sixpack.newstar_source(ns, punit=s.name,
                                                    I0=eval(v.group('col12')),
                                                    SI=[random()], f0=1e6,
                                                    RA=source_RA,
                                                    Dec=source_Dec,
                                                    fsr_trace=False,
                                                    trace=False)
         if trace: print '  -> Sixpack:',my_sixpack.label()

         # First compose the sixpack before giving it to the LSM
         SourceRoot = my_sixpack.sixpack(ns)
         # my_sixpack.display()
         lsm.add_source(s, brightness=eval(v.group('col12')),
                        sixpack=my_sixpack,
                        ra=source_RA, dec=source_Dec)
   if trace:
      print "** Inserted %d sources" % linecount

   # Finishing touches:
   lsm.setNodeScope(ns)                           # remember node scope....(!)
   lsm.save('lsm_current.lsm')                        # 
   lsm.save(lsm_name)
   lsm.display()
   if trace:
      print '** Saved as:',lsm_name,'   (and lsm_current.lsm)'
      print '**************************************************************\n'
   return True





#=================================================================================

# Create an empty global lsm, just in case:
lsm = LSM()
# lsm.display()    # QPaintDevice: Must construct a QApplication before a QPaintDevice


#=================================================================================
#=================================================================================
#=================================================================================


def arcmin2rad(arcmin=None):
   """Convert arcmin to radians"""
   factor = pi/(60*180)                         # 180/pi = 57.2957795130....
   if not arcmin==None: return arcmin*factor    # if arcmin specified, convert
   return factor                                # return conversion factor

def deg2rad(deg=None):
   """Convert deg to radians"""
   factor = pi/180                              # 180/pi = 57.2957795130....
   if not deg==None: return deg*factor          # if deg specified, convert
   return factor                                # return conversion factor



#--------------------------------------------------------------------------------

def add_single (ns=None, Sixpack=None, lsm=None, **inarg):
   """Add a test-source (Sixpack) to the given lsm"""

   qual = 'single'
   
   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_lsm::add_single()', version='10feb2006',
                           description=add_single.__doc__)
   JEN_inarg.nest(pp, MG_JEN_Sixpack.newstar_source(_getdefaults=True, _qual=qual))

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   print 'funcname =',funcname

   pp1 = MG_JEN_Sixpack.newstar_source(_getpp=True, _qual=qual)

   # Create the source defined by pp:
   Sixpack = MG_JEN_Sixpack.newstar_source(ns, _inarg=pp, _qual=qual)

   # Compose the sixpack before adding it to the lsm:
   Sixpack.sixpack(ns)
   Sixpack.display()
   lsm.add_sixpack(sixpack=Sixpack)
   # Finished:
   return True



#--------------------------------------------------------------------------------

def add_grid (ns=None, lsm=None, **inarg):
   """Add a rectangular grid of identical test-sources to the given lsm"""

   qual='grid'

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_lsm::add_grid()', version='10feb2006',
                           description=add_grid.__doc__)

   JEN_inarg.nest(pp, MG_JEN_Sixpack.newstar_source(_getdefaults=True, _qual=qual))
 
   JEN_inarg.define(pp, 'nRA2', 1, choice=[0,1,2,3],   
                    help='(half) nr of sources in RA direction')
   JEN_inarg.define(pp, 'nDec2', 1, choice=[0,1,2,3],   
                    help='(half) nr of sources in DEC direction')
   JEN_inarg.define(pp, 'dRA', 10, choice=[],    
                    help='RA grid spacing (arcmin)')
   JEN_inarg.define(pp, 'dDec', 10, choice=[],    
                    help='Dec grid spacing (arcmin)')

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   print 'funcname =',funcname

   # Get the internal argument-record for .newstar_source():
   pp1 = MG_JEN_Sixpack.newstar_source(_getpp=True, _inarg=pp, _qual=qual)
   RA0 = pp1['RA']
   Dec0 = pp1['Dec']

   # Create the sources defined by pp:
   for i in range(-pp['nRA2'],pp['nRA2']+1):
      RA = RA0 + i*pp['dRA']*arcmin2rad()
      for j in range(-pp['nDec2'],pp['nDec2']+1):
         Dec = Dec0 + j*pp['dDec']*arcmin2rad()
         punit = 'grid:'+str(i)+':'+str(j)
         Sixpack = MG_JEN_Sixpack.newstar_source(ns, _inarg=pp, _qual=qual,
                                                 punit=punit, RA=RA, Dec=Dec)
         # Compose the sixpack before adding it to the lsm:
         Sixpack.sixpack(ns)
         # lsm.add_sixpack(sixpack=Sixpack,ns=ns)
         lsm.add_sixpack(sixpack=Sixpack)
   # Finished:
   return True


#--------------------------------------------------------------------------------

def add_spiral (ns=None, lsm=None, **inarg):
   """Add a spiral pattern of identical test-sources to the given lsm"""

   qual = 'spiral'

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_lsm::add_spiral()', version='10feb2006',
                           description=add_spiral.__doc__)
   JEN_inarg.nest(pp, MG_JEN_Sixpack.newstar_source(_getdefaults=True, _qual=qual))

   JEN_inarg.define(pp, 'nr', 20, choice=[2,3,4,5,10],   
                    help='nr of sources')
   JEN_inarg.define(pp, 'rstart', 10, choice=[1,2,5,10,20,50,100],   
                    help='start position radius (arcmin)')
   JEN_inarg.define(pp, 'astart', 0, choice=[1,2,5,10,20,50,100],   
                    help='start position angle (deg)')
   JEN_inarg.define(pp, 'rmult', 1.1, choice=[1.01,1.1,1.2,1.5,2],    
                    help='radius multiplication factor')
   JEN_inarg.define(pp, 'ainc', 10, choice=[10,20,30,45,90,180,360,0],    
                    help='position angle increment (deg)')

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   print 'funcname =',funcname

   # Get the internal argument-record for .newstar_source():
   pp1 = MG_JEN_Sixpack.newstar_source(_getpp=True, _inarg=pp, _qual=qual)
   RA0 = pp1['RA']
   Dec0 = pp1['Dec']

   # Create the sources defined by pp:
   r = 0.0
   a = 0.0
   for i in range(pp['nr']):
      RA = RA0 + r*cos(a)
      Dec = Dec0 + r*sin(a)
      punit = 'spiral:'+str(i)
      Sixpack = MG_JEN_Sixpack.newstar_source(ns, _inarg=pp, _qual=qual,
                                              punit=punit, RA=RA, Dec=Dec)
      # Compose the sixpack before adding it to the lsm:
      Sixpack.sixpack(ns)
      lsm.add_sixpack(sixpack=Sixpack)

      # Calculate the position of the next source:
      if i==0:
         r = pp['rstart']*arcmin2rad()
         a = pp['astart']*deg2rad()
      else:
         r *= pp['rmult']
         a += pp['ainc']*deg2rad()
   # Finished:
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

JEN_inarg.define (MG, 'input_LSM', None, browse='*.lsm',
                  choice=['lsm_current.lsm','3c343_nvss.lsm',
                          'abel963.lsm','D1.lsm',None],
                  help='(file)name of the Local Sky Model to be used')

JEN_inarg.define (MG, 'saveAs', 'lsm_current.lsm', browse='*.lsm',
                  choice=['auto',None,'lsm_current.lsm'],
                  help='Save the (modified) LSM afterwards as...')

# Optional: add test-source(s) to the given lsm:
JEN_inarg.define (MG, 'test_pattern', None,
                  choice=[None,'single','grid','spiral'],
                  help='pattern of test-sources to be generated')
JEN_inarg.nest(MG, add_single(_getdefaults=True))
JEN_inarg.nest(MG, add_grid(_getdefaults=True))
JEN_inarg.nest(MG, add_spiral(_getdefaults=True))




#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)

# NB: Using False here does not work, because it regards EVERYTHING
#        as an orphan, and deletes it.....!?
# Settings.orphans_are_roots = True




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

   # Start with an empty lsm:
   global lsm 
   lsm = LSM()
   display_lsm = False
   save_lsm = False

   # Optional: use an existing lsm
   print '\n** MG[input_LSM] =',MG['input_LSM'],'\n'
   if MG['input_LSM']:
      lsm.load(MG['input_LSM'],ns)
      display_lsm = True
      save_lsm = True
   else:
      lsm.setNodeScope(ns)



   # Optional: add one or more test-sources to the lsm:
   if isinstance(MG['test_pattern'], str):
      display_lsm = True
      save_lsm = True
      if MG['test_pattern']=='single':
         add_single(ns, lsm=lsm, _inarg=MG)
      elif MG['test_pattern']=='grid':
         add_grid(ns, lsm=lsm, _inarg=MG)
      elif MG['test_pattern']=='spiral':
         add_spiral(ns, lsm=lsm, _inarg=MG)
      else:
         print 'test_pattern not recognised:',MG['test_pattern']

   # Save the (possibly modified) lsm under a different name:
   if MG['saveAs']:
      lsm.save(MG['saveAs'])

   # Save the lsm as 'lsm_current', for continuity:
   if save_lsm:
      lsm.save('lsm_current.lsm')

   # Display the current lsm AFTER saving (so we have the new name)
   # NB: The program does NOT wait for the control to be handed back!
   if display_lsm:
      lsm.display()

   
   # Make the trees of all the lsm punits: 
   radec = []                                 # for collect_radec()
   if True:
      plist = lsm.queryLSM(count=1000)
      print '\n** plist =',type(plist),len(plist)
      bb = []
      for i in range(len(plist)):
         punit = plist[i] 
         Sixpack = punit.getSP()              # get_Sixpack()
         if i<5:
            cc.append(MG_JEN_Sixpack.make_bookmark(ns, Sixpack, radec=radec))
         else:
            cc.append(MG_JEN_Sixpack.make_bundle(ns, Sixpack, radec=radec))
         # Actions depending on the type of source:
         if Sixpack.ispoint():                # point source (Sixpack object)
            pass
         else:	                              # patch (not a Sixpack object!)
            node = Sixpack.root()             # ONLY valid for a patch...#
            cc.append(node)                   # ....?

   # Finished: 
   MG_JEN_Sixpack.collect_radec(radec, ns=ns) # Make a radec root node (tidier)
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


def _tdl_job_nvss_3c343 (mqs, parent):
   """Create lsm(s) from nvss txt-file(s)"""
   ns = NodeScope()
   return nvss_3c343(ns)

def _tdl_job_nvss_Abell963 (mqs, parent):
   """Create lsm(s) from nvss txt-file(s)"""
   ns = NodeScope()
   return nvss_Abell963(ns)

def _tdl_job_nvss_all (mqs, parent):
   """Create lsms from all available nvss txt-file"""
   ns = NodeScope()
   return nvss_all(ns)
   



#----------------------------------------------------------------
# Obsolete?
#----------------------------------------------------------------

if False:
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

   if 0:
      igui = JEN_inargGui.ArgBrowser()
      igui.input(MG, set_open=False)
      igui.launch()
       

   if 0:
      lsm = lsm_343(ns)
      plist = lsm.queryLSM(count=3)
      for pu in plist:
         my_sp = pu.getSP()
         my_sp.display()

   if 1:
      lss = lsmSet()
      lss.display()
      lss.append()
      lss.append()
      lss.display()

   if 0:
      MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
      # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
   print '\n** End of local test of:',MG['script_name'],'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




