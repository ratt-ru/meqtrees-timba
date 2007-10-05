# file: ../Grow/TwigFlagger.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The TwigFlagger class inserts a (simple) flagger.
"""


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

from Timba.Contrib.JEN.Grow import Twig
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math



#=============================================================================
#=============================================================================

class TwigFlagger(Twig.Twig):
    """Class derived from Twig"""

    def __init__(self,
                 quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Twig.Twig.__init__(self, name='TwigFlagger',
                           quals=quals,
                           submenu=submenu,
                           OM=OM, namespace=namespace,
                           **kwargs)
        return None

    
    #====================================================================
    
    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(Twig.Twig.grow.__doc__, level=level)
        ss = Twig.Twig.derivation_tree(self, ss, level=level+1)
        return ss

    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This placeholder function should be reimplemented by a derived class.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        self.defopt('flag_oper', 'GT',
                    prompt='flag operation',
                    opt=['GT','GE','LE','LT'],
                    doc="""GT is Greater-Than, GE is Greater-or-Equal, etc
                    """)
        self.defopt('sigma', 5.0,
                    prompt='sigma',
                    opt=[1.0,2.0,3.0,5.0,7.0,9.0], more=float,
                    doc="""Flag the cells whose values deviate 'flag_oper'
                    the specified nr of 'sigmas' from the domain mean.
                    """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def grow (self, ns, node, test=None, trace=False):
        """The TwigFlagger class is derived from the Twig class.
        It can be used for flagging those cells of its input result
        that exceed a specified criterion, e.g. 3 sigma.
        """

        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        flag_oper = self.optval('flag_oper', test=test)
        sigma = self.optval('sigma', test=test)

        # Make the subtree: 
        mean = self.ns['mean'] << Meq.Mean(node)
        stddev = self.ns['stddev'] << Meq.StdDev(node)
        diff = self.ns['diff'] << Meq.Subtract(node, mean) 
        absdiff = self.ns['absdiff'] << Meq.Abs(diff) 
        crit = self.ns['crit'] << Meq.Subtract(absdiff, sigma*stddev) 

        # NB: Assume that ZeroFlagger can have multiple children....(?)
        zflag = self.ns['zflag'] << Meq.ZeroFlagger(crit, oper=flag_oper)

        # The new flags are merged with those of the input node:
        node = self.ns['mflag'] << Meq.MergeFlags(children=[node,zflag])
   
        # Optional: merge the flags of multiple tensor elements of input/output:
        ## if pp.merge: output = ns.Mflag << Meq.MergeFlags(output)

        self.bookmark([crit,zflag])

        #..............................................
        # Check the new rootnode:
        return self.on_output (node, trace=trace)





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


pgt = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    pgt = TwigFlagger()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        pgt = TwigFlagger()
        pgt.make_TDLCompileOptionMenu()

    cc = []

    node = ns << 1.0
    rootnode = pgt.grow(ns, node)
    cc.append(rootnode)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    xtor.make_TDLRuntimeOptionMenu(node=ns.result)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent)
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the Plugin object"""
    pgt.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Plugin object"""
    pgt.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        pgt = TwigFlagger()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict(flag_oper='GT')
        pgt.grow(ns, node, test=test, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================
