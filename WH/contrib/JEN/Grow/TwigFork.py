# file: ../JEN/Grow/TwigFork.py

# History:
# - 15sep2007: creation (from TwigDemo.py)

# Description:

"""The TwigFork class combines the results of two (or more?) Twig
classes into a single result (i.e. node). There are various combine
operations, e.g. Subtract, Add, ReqSeq, Composer, etc
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
from Timba.Contrib.JEN.control import Executor

from Timba.Contrib.JEN.Grow import TwigLeafParm
from Timba.Contrib.JEN.Grow import TwigLeafConstant
from Timba.Contrib.JEN.Grow import TwigLeafDimGrids
        

# import math
# import random



#=============================================================================
#=============================================================================

class TwigFork(Twig.Twig):
    """Class to combine the results of two Twig classes into one."""

    def __init__(self, quals=None,
                 name='TwigFork',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Twig.Twig.__init__(self, quals=quals,
                           name=name,
                           submenu=submenu,
                           toggle=False,
                           OM=OM, namespace=namespace,
                           **kwargs)

        # The other input (node)
        self._other = None
        return None


    #====================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = Twig.Twig.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        print prefix,'   * other =',str(self._other)
        #...............................................................
        Twig.Twig.display(self, full=full,
                          recurse=recurse,
                          OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)



    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived TwigFork classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Placeholder:
        opt = ['Subtract','Add','Multiply','Divide',
               'ReqSeq','Composer']
        self._OM.define(self.optname('combine'), 'Subtract',
                        opt=opt, more=str,
                        prompt='combine operation',
                        doc="""The input Twigs may be combined in various ways.
                        """)

        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def grow (self, ns, node, other, test=None, trace=False):
        """Specific: Make the subtree.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        combine = self.optval('combine', test=test)
        self._other = other
        result = self.ns[combine] << getattr(Meq,combine)(node,other)

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    

#=============================================================================
#=============================================================================
#=============================================================================

class TestTwigFork(Twig.Twig):
    """Class to test the class TwigFork (and leaves)"""

    def __init__(self, quals=None,
                 name='TestTwigFork',
                 submenu='compile',
                 xtor=None,
                 OM=None, namespace=None,
                 **kwargs):

        Twig.Twig.__init__(self, quals=quals,
                           name=name,
                           submenu=submenu,
                           has_input=False,
                           toggle=False,
                           OM=OM, namespace=namespace,
                           **kwargs)

        self._xtor = xtor

        return None


    
    #====================================================================
    #====================================================================

    def create_Growth_objects (self, trace=False):
        """Specific: Create any Growth objects, sharing the OptionManager
        """
        rr = self._Growth_objects
        rr['fork2'] = TwigFork('2', submenu=self._submenu, OM=self._OM)
        rr['leaf3'] = TwigLeafDimGrids.TwigLeafDimGrids(submenu=rr['fork2']._submenu,
                                                  OM=self._OM, xtor=self._xtor)
        rr['fork1'] = TwigFork('1', submenu=rr['fork2']._submenu, OM=self._OM)
        rr['leaf1'] = TwigLeafConstant.TwigLeafConstant(submenu=rr['fork1']._submenu,
                                                        OM=self._OM)
        rr['leaf2'] = TwigLeafParm.TwigLeafParm(submenu=rr['fork1']._submenu, OM=self._OM)
        return True
        
    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """Specific: Make the subtree.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        rr = self._Growth_objects
        result = rr['fork1'].grow(ns,
                                  rr['leaf1'].grow(ns),
                                  rr['leaf2'].grow(ns))
        result = rr['fork2'].grow(ns,
                                  result,
                                  rr['leaf3'].grow(ns))

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 1:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    plf = TestTwigFork(xtor=xtor)
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = TestTwigFork(xtor=xtor)
        plf.make_TDLCompileOptionMenu()

    cc = []

    rootnode = plf.grow(ns)
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
    """Just display the current contents of the Twig object"""
    plf.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Twig object"""
    plf.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 0:
        plf = TwigFork()
        plf.display('initial')

    if 1:
        plf = TestTwigFork()
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 0:
        node = ns << 1.2
        other = ns['other'] << -1.2
        test = dict()
        plf.grow(ns, node, other, test=test, trace=False)

    if 1:
        test = dict()
        plf.grow(ns, test=test, trace=False)

    if 1:
        plf.display('final', OM=True, full=True)




#===============================================================

