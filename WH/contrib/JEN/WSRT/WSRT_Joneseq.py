# file: ../WSRT/WSRT_Joneseq.py

# History:
# - 15jun2007: creation (from Grunting/WSRT_Jones.py)

# Description:

# Make a matrix product of a sequence 2x2 WSRT Jones matrices. The
# result is a Jones matrix object, derived from Grunt.Joneset22.

# Copyright: The MeqTree Foundation


#======================================================================================
# Preamble:
#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.WSRT import WSRT_JJones
from Timba.Contrib.JEN.WSRT import WSRT_GJones
from Timba.Contrib.JEN.WSRT import WSRT_FJones
from Timba.Contrib.JEN.WSRT import WSRT_DJones
from Timba.Contrib.JEN.WSRT import WSRT_BJones
# from Timba.Contrib.JEN.WSRT import WSRT_EJones



#=================================================================================================
# Functions to streamline the use of WSRT Jones matrices: 
#=================================================================================================

def help ():
    ss = 'help on WSRT Jones matrices'
    return ss



#------------------------------------------------------------------------------------------

def Joneseq22_uvp(ns, stations, jseq=None, simulate=False, override=None):
    """Return a Jonest22 object that contains a set of Jones matrices for
    the given stations. This function deals with uv-plane effects only.
    The Jones matrices are the matrix product of a
    sequence of WSRT Jones matrices that are defined in this module.
    - The 'TDL_' arguments in this function are user-defined in the meqbrowser,
    via the TDLOptions defined in the function .include_TDL_options() in this module.
    - The sequence is defined by the letters (e.g. 'GD') of the string TDL_joneseq.
    - If simulate==True, the Jones matrices do not contain MeqParms,
    but subtrees that simulate MeqParm values that change with time etc."""

    # If not specified, use the TDLOption value:
    if jseq==None: jseq = TDL_jseq
    # print '** jseq=',jseq,' simulate=',simulate,'\n'

    # If jseq==None or [], do nothing (return unit matrix?)
    if not jseq: return None

    # First make a sequence (list jj) of Joneset22 objects:
    jj = []
    for jchar in jseq:
        if jchar=='G':
            jj.append(WSRT_GJones.GJones(ns, stations=stations,
                                         override=override,
                                         simulate=simulate))
        elif jchar=='D':
            jj.append(WSRT_DJones.DJones(ns, stations=stations,
                                         override=override,
                                         simulate=simulate))
        elif jchar=='F':
            jj.append(WSRT_FJones.FJones(ns, stations=stations,
                                         override=override,
                                         simulate=simulate))
        elif jchar=='J':
            jj.append(WSRT_JJones.JJones(ns, stations=stations,
                                         override=override,
                                         simulate=simulate))
        elif jchar=='B':
            jj.append(WSRT_BJones.BJones(ns, stations=stations,
                                         override=override,
                                         simulate=simulate))
        else:
            raise ValueError,'WSRT jones matrix not recognised: '+str(jchar)

    # Then matrix-multiply them into a single Joneset22 object:
    jones = Joneset22.Joneseq22(ns, jj)
    return jones



#============================================================================
# TDL Options:
#============================================================================

# TDLCompileOptionSeparator()

_jseq_option = TDLCompileOption('TDL_jseq',"Selected Jones matrix sequence",
                                ['J','G','F','J','B','GD','GDF','GDFJB',None],
                                more=str);

# Make a dict of named option-menu-objects for the various Jones matrices: 
rr = dict(G=TDLCompileMenu('Options for WSRT_GJones', WSRT_GJones),
          D=TDLCompileMenu('Options for WSRT_DJones', WSRT_DJones),
          F=TDLCompileMenu('Options for WSRT_FJones', WSRT_FJones),
          J=TDLCompileMenu('Options for WSRT_JJones', WSRT_JJones),
          B=TDLCompileMenu('Options for WSRT_BJones', WSRT_BJones))
# 
_matrix_option_menu = TDLCompileMenu('Jones matrix options',
                                     rr['G'],
                                     rr['D'],
                                     rr['F'],
                                     rr['J'],
                                     rr['B'],
                                     );

# Show/hide option menus based on selected Jones matrix sequence (jseq)

def _show_matrix_option_menus (jseq):
    if jseq==None: jseq = []
    for jchar in rr.keys():
        rr[jchar].show(jchar in jseq)
_jseq_option.when_changed(_show_matrix_option_menus);




#==========================================================================

def get_solvable_parmgroups(trace=True):
    """Return a list of selected solvable parmgroups."""
    jseq = _jseq_option.value
    if jseq==None: jseq = []
    if trace: print '\n** get_solvable_parmgroups: jseq =',jseq
    pg = []
    for jchar in ss.keys():
        if trace: print '  -',jchar,':',ss[jchar].value
        if jchar in jseq:
            pg.append(ss[jchar].value)
    if trace: print '   -> pg =',pg 
    return pg
            
#--------------------------------------------------------------------------

def make_solv_option_menu():
    """Should be called before making the module submenu"""
    
    # Make a dict of TDLOption objects:
    global ss
    ss = dict(G=WSRT_GJones.TDL_parmgroups(),
              D=WSRT_DJones.TDL_parmgroups(),
              F=WSRT_FJones.TDL_parmgroups(),
              J=WSRT_JJones.TDL_parmgroups(),
              B=WSRT_BJones.TDL_parmgroups())

    # Make TDL options for (groups of) solvable parms:
    _solv_option_menu = TDLCompileMenu('Jones solvable parmgroups',
                                       ss['G'],
                                       ss['D'],
                                       ss['F'],
                                       ss['J'],
                                       ss['B'],
                                       # toggle='TDL_solve',
                                       );

    # Show/hide option menus based on selected Jones matrix sequence (jseq)
    def _show_solv_option_menus (jseq):
        if jseq==None: jseq = []
        for jchar in ss.keys():
            ss[jchar].show(jchar in jseq)
            if jchar in jseq:
                print '** jchar =',jchar,' current value =',ss[jchar].value
    _jseq_option.when_changed(_show_solv_option_menus);

    # Finished:
    return _solv_option_menu






     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []
    stations = range(3)

    jones = Joneseq22_uvp(ns, stations, simulate=True, override=None)

    cc.append(jones.visualize('*'))
    cc.append(jones.p_plot_rvsi())
    cc.append(jones.p_bundle())
    cc.append(jones.bundle())
    jones.display(full=True)

    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,1000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       



#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        stations = range(3)
        jseq = 'GD'
        jones = Joneseq22_uvp(ns, stations, jseq=jseq, simulate=False, override=None)

    if 0:
        jones.visualize('*')
        jones.p_plot_rvsi()
        jones.p_bundle()
        jones.bundle()

    if 1:
        jones.display(full=True)


#===============================================================
    
