# file: ../Grunt/solving22.py

# History:
#   19jan2007: creation
#   01apr2007: adaptation to QualScope etc

# Description:

# The solving22 module contains routines for solving for parameters
# in Matrixet22 objects. 

#======================================================================================

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

from Timba.Contrib.JEN.Grunt import Condexet22
from Timba.Contrib.JEN.Grunt import Matrixet22

from Timba.Contrib.JEN.util import JEN_bookmarks

import Meow
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..

from copy import deepcopy



#======================================================================================

def include_TDL_options(prompt=None):
    """Definition of variables that the user may set in the browser TDL options menu.
    These values are picked up by the function .make_solver() in this module."""
    menuname = 'solver options'
    if prompt: menuname += ' ('+str(prompt)+')'
    # pp = Meow.Utils.solver_options()
    pp = JEN_Meow_Utils.solver_options()                 # ..temporary..
    TDLCompileMenu(menuname, *pp)
    return True


#======================================================================================

def make_solver (lhs=None, rhs=None, parmgroup='*', 
                 quals=None, redun=None, accu=True, **pp):
    """Make a solver that solves for the specified parmgroup(s), by comparing the
    matrices of one Matrixet22 object (lhs) with the corresponding matrices of
    another (rhs).
    If rhs==None, do do a redundancy-solution, i.e. compare redundant spacings.
    If accu==True, attach the solver reqseq to the lhs accumulist."""

    ns = lhs.ns()._derive(append=quals)
    if rhs:
        ns = ns._merge(rhs.ns())
        # quals = lhs.quals(append=qual, merge=rhs.quals())
        # Accumulate nodes to be executed sequentially later:
        if accu: lhs.merge_accumulist(rhs)
        # NB: Use the ParmGroupManger from the rhs (assumed predicted) Matrixet22
        #     object, NOT from the lhs (assumed measured data) ....(?)
        pgm = rhs.ParmGroupManager()
    else:
        # Redundancy-solution (rhs==None):
        # quals = lhs.quals(append=quals)
        # NB: Use the ParmGroupManger from the lhs (measured data) Matrixet22
        pgm = lhs.ParmGroupManager()

    # pgm.display('solving22')
    print pgm.tabulate(parmgroup)
        
    # Get the list of MeqParm nodes to be solved for.
    solver_label = pgm.solver_label(parmgroup)
    solvable = pgm.solvable(parmgroup)
    

    # Get the names of the (subset of) matrix elements to be used:
    # (e.g. for GJones, we only use ['m11','m22'], etc)
    matrel = lhs._matrel.keys()          # i.e. ['m11','m12','m21','m22']
    #===================================================
    if False:
        matrel = pgm.rider(parmgroup, 'matrel')      # requires a little thought.....
        if matrel=='*': matrel = lhs._matrel.keys()
    # matrel = ['m11','m22']
    # matrel = ['m11']
    #===================================================

    # Make a list of condeq nodes, by comparing either the
    # corresponding ifrs in the lhs and rhs Vissets,
    # or redundant spacings in lhs (if rhs==None):
    cdx = Condexet22.Condexet22(lhs=lhs, quals=quals)
    if rhs:
        cdx.make_condeqs (rhs=rhs, unop=None)
        condeqs = cdx.get_condeqs(matrel=matrel)
    else:
        # If no rhs, assume that redun (dict) is supplied. (See Condexet22.py)
        cdx.make_redun_condeqs (redun=redun, unop=None)         
        condeqs = cdx.get_condeqs(matrel=matrel)
        if True:
            constr = pgm.constraint_condeqs(parmgroup)
            if len(constr)>0: condeqs.extend(constr)


    # Create the solver:

    # The solver writes (the stddev of) its condeq resunts as ascii
    # into a debug-file (SBY), for later visualisation.
    # - all lines start with the number of entries (one per condeq)
    # - the first line has the condeq names (solver children)
    # - the rest of the lines have one ascii number per condeq
    # - Q: the solver writes a line at each iteration...? 
    # NB: the extension can be chosen at will, for identification
    debug_file = 'debug_'+str(qual)+'.ext'

    # sopt = Meow.Utils.create_solver_defaults()
    sopt = JEN_Meow_Utils.create_solver_defaults()        # temporary
    sopt.__delitem__('solvable')
    
    name = 'solver'+solver_label
    solver = ns[name] << Meq.Solver(children=condeqs, 
                                    # debug_file=debug_file,
                                    # parm_group=hiid(parm_group),
                                    # child_poll_order=cpo,
                                    solvable=solvable, **sopt)

    # Bundle (cc) the solver and its related visualization dcolls
    # for attachment to a reqseq (below).
    
    cc = []
    cc.append(solver)
    bookpage = 'solver'+solver_label
    JEN_bookmarks.create(solver, page=bookpage)
    
    # Visualize the groups of solvable MeqParms:
    cc.append(pgm.visualize(parmgroup))
    
    # Visualize the condeqs:
    condequal = 'condeq'+solver_label+ns._qualstring()
    # if isinstance(qual,(list,tuple)):
    #     condequal = qual
    #     condequal.insert(0,'condeq'+solver_label)
    # elif isinstance(qual,str):
    #     condequal = [condequal,qual]
    dcoll = cdx.visualize(condequal, matrel=matrel, bookpage=bookpage, visu='*')
    cc.append(dcoll)

    # Bundle solving and visualisation nodes:
    name = 'reqseq_solver'+solver_label
    reqseq = ns[name] << Meq.ReqSeq(children=cc)
    if accu: lhs.accumulist(reqseq)

    # Return the solver reqseq (usually not used if accu==True):
    return reqseq
        
    


     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

# Meow.Utils.solver_options()
# include_TDL_options()

def _define_forest(ns):

    cc = []
    simulate = True

    mat1 = Matrixet22.Matrixet22(ns, quals=[], simulate=True)
    mat1.test()
    mat1.display(full=True)

    mat2 = Matrixet22.Matrixet22(ns, quals=[], simulate=False)
    mat2.test()
    mat2.visualize()
    mat2.display(full=True)

    reqseq = make_solver(lhs=mat1, rhs=mat2)
    cc.append(reqseq)

    if True:
        aa = mat1.accumulist()
        aa.extend(mat2.accumulist())
        print 'aa=',aa
        node = ns.accu << Meq.Composer(children=aa)
        cc.append(node)

    ns.result << Meq.ReqSeq(children=cc)
    # ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        pp = include_TDL_options()

    if 1:
        m1 = Matrixet22.Matrixet22(ns, quals=['3c84','xxx'], label='HH')
        m1.test()
        m1.visualize()
        m1.display(full=True)

        m2 = Matrixet22.Matrixet22(ns, quals=['3c84','yyy'], label='TT')
        m2.test()
        m2.display('m2',full=True)

        reqseq = make_solver(lhs=m1, rhs=m2, accu=True)
        m1.display('after make_solver()', full=True)
        m1._dummyParmGroup.display_subtree (reqseq, txt='solver_reqseq',
                                            show_initrec=False, recurse=3)
        


#===============================================================
    
