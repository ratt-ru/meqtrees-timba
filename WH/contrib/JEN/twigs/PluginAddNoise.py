# file: ../twigs/PluginAddNoise.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The PluginAddNoise class makes makes a subtree that takes an input node and
produces a new rootnode by .....
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

from Timba.Contrib.JEN.twigs import Plugin
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math



#=============================================================================
#=============================================================================

class PluginAddNoise(Plugin.Plugin):
    """Class derived from Plugin"""

    def __init__(self, quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, quals=quals,
                               name='PluginAddNoise',
                               submenu=submenu,
                               OM=OM, namespace=namespace,
                               **kwargs)
        return None

    
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................
        self._OM.define(self.optname('stddev'), None,
                        prompt='stddev',
                        opt=[0.1,1.0], more=float,
                        doc="""add gaussian noise (if stddev>0)
                        """)
        self._OM.define(self.optname('datatype'), 'auto',
                        prompt='noise data type',
                        opt=['auto','real','complex','polar'], 
                        doc="""specify the data-type of the added noise.
                        - If 'auto', the type is determined by the type
                        of the result to which the noise is added.
                        - If 'complex', the real and imag parts are noisy.
                        - If 'polar', the ampl and phase are noisy.
                        """)
        #..............................................
        return self.on_exit(trace=trace)



    #====================================================================

    def make_subtree (self, ns, node, test=None, trace=True):
        """Specific: Make the plugin subtree.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        if test==True:
            test = dict(stddev=1.0)

        # Read the specified options:
        stddev = self.optval('stddev', test=test)
        if not stddev or stddev<=0.0:
            return self.bypass (trace=trace)
        datatype = self.optval('datatype', test=test)

        if datatype=='auto':
            if self.datadesc()['is_complex']:
                datatype = 'complex'
            else:
                datatype = 'real'

        # Make the subtree:
        name = 'stddev~'+str(stddev)
        if datatype=='complex':
            real = self.ns['real'] << Meq.GaussNoise(stddev=stddev)
            imag = self.ns['imag'] << Meq.GaussNoise(stddev=stddev)
            noise = self.ns[name] << Meq.ToComplex(real,imag)
        elif datatype=='polar':
            ampl = self.ns['ampl'] << Meq.GaussNoise(stddev=stddev)
            phase = self.ns['phase'] << Meq.GaussNoise(stddev=stddev)
            noise = self.ns[name] << Meq.ToPolar(ampl,phase)
        else:
            noise = self.ns[name] << Meq.GaussNoise(stddev=stddev)
        node = self.ns['+'+name] << Meq.Add(node,noise)

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
    pgt = PluginAddNoise()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        pgt = PluginAddNoise()
        pgt.make_TDLCompileOptionMenu()

    cc = []

    node = xtor.leafnode(ns)
    rootnode = pgt.make_subtree(ns, node)
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
        pgt = PluginAddNoise()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict(stddev=1.0, datatype='polar')
        pgt.make_subtree(ns, node, test=test, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================

