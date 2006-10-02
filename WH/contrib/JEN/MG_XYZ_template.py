# MG_XYZ_template.py

# Short description:
#   A template for the generation of MG stripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 15 sep 2006: creation

# Copyright: The MeqTree Foundation

# Full description:

# MG scripts should (roughly) have the following parts:
# - PART   I: Organised specific information about this script
# - PART  II: Preamble (import etc) and initialisation (if any)
# - PART III: Optional: Importable functions (to be used by other scripts)
# - PART  IV: Required: Test/Demo function _define_forest(), called from the meqbrowser
# - PART   V: Forest execution routine(s), called from the meqbrowser
# - PART  VI: Recommended: Standalone test routines (no meqbrowser or meqserver)

# This template is a regular MG script, which may be executed from the
# browser (to see how things work).  It is hoped that it will lead to
# a large collection of user-contributed scripts, which are readily
# accessible to all via the MeqTree 'Water Hole'.

# How to use this template:
# - Copy it to a script file with a name like this:
#      MG_<authorinitials>_<function>.py
# - Put it into your Water Hole sub-directory:
#      /Timba/WH/contrib/<author initials>/
# - Fill in the correct script_name (and other info) at the top of part I and II
# - Fill in the author and the short (one-line) description
# - Replace the full description with a specific one
# - Replace the example importable function with specific ones
# - Make the specific _define_forest() function. Try to make this
#   a complete test and demonstration of all its importable functions.
# - Write lots of explanatory comments throughout, preferably in the
#   form of Python 'doc-strings' at the start of each function.
# - Test everything thoroughly, without and with the browser.
# - Make it known to your MG_XYZ_testall.py script (see MG_XYZ_testall.py)
# - Check it in via SVN. After that, it is available to all,
#   and visible to the MG catalog and testing systems

# Of course, it is also possible, and often preferrable to just copy a
# working script from someone else, and cannibalise it.

   




 
#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

# from qt import *
# from numarray import *
# from string import *
# from copy import deepcopy

# Make sure that all nodes retain their results in their caches,
# for your viewing pleasure.
Settings.forest_state.cache_policy = 100


# NB: Demonstrate the OMS parameter system here (because it has browser support)?


#********************************************************************************
#********************************************************************************
#******************** PART III: Optional: Importable functions ******************
#********************************************************************************
#********************************************************************************







#********************************************************************************
#********************************************************************************
#**************** PART IV: Required test/demo function **************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Make two 'leaf' nodes that show some variation over freq/time. 
   a = ns['a'] << Meq.Time()
   b = ns['b'] << Meq.Freq()

   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Add(a,b)

   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result', viewer='Result Plotter',
               udi='/node/result', publish=True)
   Settings.forest_state.bookmarks = [bm]

   # Finished:
   return True



# Ideas for demo/assignment scripts:
# - demo_template.py:           low threshold, uniformity
# - demo_onDefineEntry.py:            avoid clutter
# - demo_onDefineExit.py:             avoid clutter

# - demo_myFirstTree.py:
# - demo_request.py:            4D           
# - demo_errors.py:
# - demo_nodeNames.py:          scope, duplicate names

# - demo_allBinop.py:
# - demo_allUnop.py:

# - demo_leaves.py:             make some of them part of TDL?
#     freq, time, l, m, 'grid', gauss, random, constant, parm, complex

# - demo_tensor.py:
#     behaviour of mean etc!
# - demo_matrix22.py
#     check of inverse

# - demo_reqseq.py:
# - demo_reqmux.py:

# - demo_parm.py:
# - demo_solve.py:

# - demo_expression.py:
# - demo_voltage_beam.py:
 
# - demo_composer.py:
# - demo_fitsImage.py:

# - demo_dataCollect.py:
# - demo_historyCollect.py:

# - demo_flag.py:

# - demo_MS.py:
# - demo_jones.py:
# - demo_lsm.py:


# Unop:
#   1336 2006-09-14 14:36 Exp.cc
#   1294 2006-09-14 14:36 Log.cc
#   1298 2006-09-14 14:36 Negate.cc
#   1304 2006-09-14 14:36 Invert.cc
#   1349 2006-09-14 14:36 Sqrt.cc
#   1334 2006-09-14 14:36 Sqr.cc

#   1367 2006-09-14 14:36 Pow.cc
#   1218 2006-09-14 14:36 Pow2.cc
#   1220 2006-09-14 14:36 Pow3.cc
#   1218 2006-09-14 14:36 Pow4.cc
#   1218 2006-09-14 14:36 Pow5.cc
#   1218 2006-09-14 14:36 Pow6.cc
#   1218 2006-09-14 14:36 Pow7.cc
#   1218 2006-09-14 14:36 Pow8.cc

#   1284 2006-09-14 14:36 Arg.cc
#   1346 2006-09-14 14:36 Conj.cc
#   1288 2006-09-14 14:36 Norm.cc
#   1293 2006-09-14 14:36 Real.cc
#   1298 2006-09-14 14:36 Imag.cc

#   1334 2006-09-14 14:36 Cos.cc
#   1332 2006-09-14 14:36 Sin.cc
#   1283 2006-09-14 14:36 Tan.cc
#   1294 2006-09-14 14:36 Acos.cc
#   1292 2006-09-14 14:36 Asin.cc
#   1295 2006-09-14 14:36 Atan.cc
#   1354 2006-09-14 14:36 Cosh.cc
#   1299 2006-09-14 14:36 Sinh.cc
#   1302 2006-09-14 14:36 Tanh.cc

#   1298 2006-09-14 14:36 Fabs.cc
#   1290 2006-09-14 14:36 Abs.cc
#   1306 2006-09-14 14:36 Ceil.cc
#   1316 2006-09-14 14:36 Floor.cc

# Binop:
#   1367 2006-09-14 14:36 Pow.cc
#   1373 2006-09-14 14:36 Polar.cc
#   1409 2006-09-14 14:36 ToComplex.cc
#   1395 2006-09-14 14:36 Add.cc
#   1903 2006-09-14 14:36 Multiply.cc
#   1367 2006-09-14 14:36 Divide.cc
#   1479 2006-09-14 14:36 Subtract.cc

# Leaves:
#   5691 2006-09-14 14:36 Constant.cc
#   2201 2006-09-14 14:36 Freq.cc
#   2193 2006-09-14 14:36 Time.cc
#   3008 2006-09-14 14:36 Grid.cc
#   2466 2006-09-14 14:36 GridPoints.cc
#    759 2006-09-14 14:36 NoiseNode.cc
#   3568 2006-09-14 14:36 RandomNoise.cc
#     64 2006-09-14 14:36 BlitzRandom.cc
#   3432 2006-09-14 14:36 GaussNoise.cc
#                         Spigot?
#                         TDL_Leaves....?

# Solving:
#  55515 2006-09-14 14:36 Solver.cc
#   7443 2006-09-14 14:36 Condeq.cc
#  29654 2006-09-14 14:36 Parm.cc
#  12215 2006-09-14 14:36 ParmDBInterface.cc
#  18593 2006-09-14 14:36 ParmTable.cc

# Tensor ops:
#   3500 2006-09-14 14:36 Composer.cc
#   5174 2006-09-14 14:36 Paster.cc
#   5654 2006-09-14 14:36 Selector.cc

# Tensor/cell ops:
#   1306 2006-09-14 14:36 StdDev.cc
#   1426 2006-09-14 14:36 Sum.cc
#   1920 2006-09-14 14:36 Min.cc
#   1921 2006-09-14 14:36 Max.cc
#   1257 2006-09-14 14:36 Rms.cc
#   1817 2006-09-14 14:36 Mean.cc
#   1935 2006-09-14 14:36 WMean.cc
#   1448 2006-09-14 14:36 Product.cc
#   2391 2006-09-14 14:36 WSum.cc
#   1747 2006-09-14 14:36 NElements.cc

# Matrix ops:
#   1511 2006-09-14 14:36 Identity.cc
#   3039 2006-09-14 14:36 Transpose.cc
#  16019 2006-09-14 14:36 MatrixMultiply.cc
#   7603 2006-09-14 14:36 MatrixInvert22.cc
#   3139 2006-09-14 14:36 Stokes.cc            ??

# Flow:
#   5519 2006-09-14 14:36 ReqSeq.cc
#   2790 2006-09-14 14:36 ReqMux.cc
#                         Sink, Visdatamux?

# FITS interface:
#  11971 2006-09-14 14:36 FITSDataMux.cc
#  52533 2006-09-14 14:36 FITSUtils.cc
#   1865 2006-09-14 14:36 FITSSpigot.cc
#   3909 2006-09-14 14:36 FITSWriter.cc
#   8607 2006-09-14 14:36 FITSImage.cc
#   5932 2006-09-14 14:36 FITSReader.cc
#                         shapelets?

# Flagging:
#   4474 2006-09-14 14:36 ZeroFlagger.cc
#   4311 2006-09-14 14:36 MergeFlags.cc

# Visualization:
#   4572 2006-09-14 14:36 DataCollect.cc
#   4245 2006-09-14 14:36 DataConcat.cc
#   4197 2006-09-14 14:36 HistoryCollect.cc
#   2208 2006-09-14 14:36 Stripper.cc

# Resampling:
#   9035 2006-09-14 14:36 ModRes.cc
#  52063 2006-09-14 14:36 Resampler.cc

# Domain change:
#  33244 2006-09-14 14:36 Compounder.cc

# Expression:
#   7487 2006-10-02 10:29 PrivateFunction.cc
#   7538 2006-09-14 14:36 CompiledFunklet.cc
#   8445 2006-09-14 14:36 Functional.cc

# uvbrick:
#  18887 2006-09-14 14:36 UVBrick.cc
#  19146 2006-09-14 14:36 FFTBrick.cc
#  38778 2006-09-14 14:36 UVInterpol.cc
#  46655 2006-09-14 14:36 UVInterpolWave.cc
#  10251 2006-09-14 14:36 PatchComposer.cc

# Coordinates:
#   2553 2006-09-14 14:36 LMN.cc
#   5454 2006-09-14 14:36 UVW.cc
#   4235 2006-09-14 14:36 VisPhaseShift.cc
#   5212 2006-10-02 10:29 AzEl.cc
#   3883 2006-10-02 10:29 LMRaDec.cc
#   4926 2006-10-02 10:29 ParAngle.cc

# Misc:
#   8386 2006-09-14 14:36 ReductionFunction.cc





#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

# The function with the standard name _test_forest(), and any function
# with name _tdl_job_xyz(m), will show up under the 'jobs' button in
# the browser, and can be executed from there.  The 'mqs' argument is
# a meqserver proxy object.
# NB: The function _test_forest() is always put at the end of the menu:

def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    trace = True
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    if trace: print '\n** domain =',domain
    cells = meq.cells(domain, num_freq=10, num_time=11)
    if trace: print '\n** cells =',cells
    request = meq.request(cells, rqtype='ev')
    if trace: print '\n** request =',request
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    if trace: print '\n** result =',result,'\n'
    return result


def _tdl_job_incl_zero (mqs, parent):
    """Execute the forest with a domain that includes f=0 and t=0"""
    domain = meq.domain(0,10,0,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result

def _tdl_job_incl_negative (mqs, parent):
    """Execute the forest with a domain that includes f<0 and t<0"""
    domain = meq.domain(-1,10,-10,10)                         # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result


def _tdl_job_sequence(mqs, parent):
   """Execute the forest for a sequence of requests with changing domains"""
   trace = True
   for x in range(10):
       domain = meq.domain(x,x+1,x,x+1)                       # (f1,f2,t1,t2)
       if trace: print '\n** x =',x,': -> domain =',domain
       cells = meq.cells(domain, num_freq=20, num_time=19)
       request = meq.request(cells, rqtype='ev')
       result = mqs.meq('Node.Execute',record(name='result', request=request0))
   return True


# NB: If you execute one after the other without recompiling first,
#     the domain does not change!!



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_XYZ_template.py

if __name__ == '__main__':
   print '\n*******************\n** Local test of: MG_XYZ_template.py :\n'

   ns = NodeScope()


   print '\n** End of local test of: MG_XYZ_template.py \n*******************\n'
       
#********************************************************************************
#********************************************************************************




