# file: ../JEN/Grow22/Jseq22.py

# History:
# - 14oct2007: creation (from TwigBranch.py)

# Description:

"""The Jseq22 class is derived from the J22 class. It allows the user to construct
a set of station Jones matrices by multiplying a sequence of Jones matrices.
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


from Timba.Contrib.JEN.Grow22 import J22
from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.control import Executor




#=============================================================================
#=============================================================================

class Jseq22(J22.J22):
    """Class derived from J22"""

    def __init__(self, quals=None,
                 name='Jseq22',
                 submenu='compile',
                 solvermenu=None,
                 OM=None, namespace=None,
                 **kwargs):

        J22.J22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         solvermenu=solvermenu,
                         OM=OM, namespace=namespace,
                         defer_compile_options=True,
                         **kwargs)

        # Initialize the J22 sequence:
        self._jones_order = []
        self._jones = dict()

        return None


    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(J22.J22.grow.__doc__, level=level)
        ss = J22.J22.derivation_tree(self, ss, level=level+1)
        return ss

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = J22.J22.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('Jseq22', level=level, txt=txt)
        #...............................................................
        print prefix,'  * Jones sequence (+ is selected):'
        for key in self._jones_order:
            rr = self._jones[key]
            if rr['jones']._OMI.is_selected():
                print prefix,'    + '+key+': '+str(rr['jones'].oneliner())
            else:
                print prefix,'    - '+key+': '+str(rr['jones'].oneliner())
        #...............................................................
        J22.J22.display(self, full=full,
                        recurse=recurse,
                        OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)


    #====================================================================
    # Generic part:
    #====================================================================


    def add_jones(self, module, quals, submenu, modes=None, trace=False):
        """
        Check the given J22 object, and add it to self._jones.
        """

        if trace:
            print '\n** .add_jones(',type(module),quals,submenu,modes,'):'
                        

        jones = module(quals, submenu=submenu,
                       solvermenu=self._solvermenu,
                       OM=self._OM,
                       stations=self.stations(),
                       polrep=self.polrep(),
                       inhibit_selection=self._kwargs['inhibit_selection'],
                       toggle_box=True)
        print type(jones)
        print jones.oneliner()

        # OK, add the valid jones to the list:
        name = jones.name
        self._jones[name] = dict(jones=jones, modes=modes) 
        self._jones_order.append(name)

        if trace:
            print '   ->',jones.oneliner()
        return True


    #---------------------------------------------------------------------------

    def create_Growth_objects (self, trace=False):
        """Re-implementation of the generic Growth function.
        """

        submenu = self._submenu+'.J22'
        if trace:
            print '\n** .create_Growth_objects(): submenu=',submenu
        self.define_jones_sequence (submenu, trace=trace)
        self._OM.set_menurec(submenu, prompt='select a jones sequence')

        # Execute the deferred function:
        self.define_compile_options()
        return True
        

    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The Jseq22 class is derived from the J22 class, and produces a
        Grunt.Joneset22 object that is a product of one or mode Jones matrices.  
        It is itself a baseclass for all kinds of specific Jones sequences. 
        NB: This .grow() function is generic, and should be called from the
        re-implemented .grow() function in classes derived from Jseq22.
        The specific __doc__ string of the latter is used for documentation.
        """

        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        TRACE = False
        if TRACE or trace:
            print '\n** Jseq22.grow():'

        self.display('start of .grow()')

        # First make a list (jj) of Joneset22 objects from the selected
        # J22 objects in self._jones:
        jj = []
        for key in self._jones_order:
            rr = self._jones[key]
            if TRACE or trace:
                print '--',key,':',rr['jones'].oneliner()
            j22 = rr['jones'].grow(self.ns, trace=trace)
            if TRACE or trace:
                print '   -> j22 =',type(j22)
            if j22:                                       # None if not selected...
                if TRACE or trace:
                    print '   ->',j22.oneliner()
                jj.append(j22)                            # Joneset object

        if TRACE or trace:
            print

        if len(jj)==0:
            raise ValueError,'Jones sequence is empty'
        
        # If only one Jones matrix, multiplication is not necessary:
        if len(jj)==1:
            result = jj[0]       

        else:
            # Multiply two or more Jones matrices:
            qnode = self.ns[self.name]                   
            if not qnode.must_define_here(self):
                s = '** '+str(self.name)+': nodename clash: '+str(qnode)
                raise ValueError, s

            # Multiply station-by-station:
            for station in self.stations():
                cc = []
                for k in range(len(jj)):
                    node = jj[k](station)
                    cc.append(node)
                qnode(station) << Meq.MatrixMultiply(*cc)

            # Make a merged ParmGroupManager:
            # print '\n** merging PGM:'
            PGM = jj[0]._PGM
            # PGM.display('merge: copied from jj[0]')
            for k in range(1,len(jj)):
                PGM.merge(jj[k])
                PGM.display('after merging: k='+str(k))
                    
            # Create a new Joneset22 object, and fill it:
            result = Joneset22.Joneset22(self.ns, self._OMI.name,
                                         # quals=self._OMI._quals,
                                         stations=self.stations(),
                                         polrep=self.polrep())
            result.matrixet(new=qnode) 
            result._PGM = PGM                            # transfer the merged PGM
            if TRACE or trace:
                result.display(full=True)


        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)





    #====================================================================
    # Specific part (derived classes):
    #====================================================================

    def help_specific (self):
        """Specific function to format a string with specific help for this
        object, if any.
        """

        ss += '\n*****************************************'
        ss += '\n** Sequence of available jones matrices:'
        ss += '\n*****************************************'

        for key in self._jones_order:
            rr = self._jones[key]['jones']
            ss += rr.help(specific=False, trace=False)

        return ss

    #------------------------------------------------------------------

    def grow_specific (self, ns, test=None, trace=False):
        """The XYZJseq22 class is derived from the Jseq22 class.
        It deals with a sequence of Jones matrices.
        """
        return Jseq22.Jseq22.grow(self, ns=ns, test=test, trace=trace)



    #---------------------------------------------------------------------------

    def define_jones_sequence (self, submenu, trace=False):
        """
        Define a specific sequence of J22 objects, to be used (or ignored).
        For instance GJ22, and DJ22 and FJ22.
        Placeholder, to be re-implemented by classes derived from Jseq22.
        """

        if trace:
            print '\n** define_jones_sequence(',submenu,'):'
            print '  stations = ',self.stations()

        # Import the relevant modules:
        from Timba.Contrib.JEN.Grow22 import GJ22

        # Make the jones objects:
        self.add_jones (GJ22.GJ22, '3c84', submenu=submenu)
        self.add_jones (GJ22.GJ22, '3c10', submenu=submenu)
        return True




#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


jsq = None
if 1:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    jsq = Jseq22(stations=range(1,4))
    jsq.make_TDLCompileOptionMenu()
    # jsq.display('outside')


def _define_forest(ns):

    global jsq,xtor
    if not jsq:
        xtor = Executor.Executor()
        jsq = Jseq22(stations=range(1,4))
        jsq.make_TDLCompileOptionMenu()

    cc = []

    j22 = jsq.grow(ns)
    rootnode = j22.bundle()
    print 'rootnode =',str(rootnode)
    if is_node(rootnode):
        cc.append(rootnode)

    if len(cc)==0:
        cc.append(ns.dummy<<1.1)
    print '** cc =',cc
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
    """Just display the current contents of the J22 object"""
    jsq.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the J22 object"""
    jsq.display('_tdl_job', full=True)
       
def _tdl_job_print_tree (mqs, parent):
    """Just display the current contents of the J22 object"""
    jsq.print_tree()

def _tdl_job_derivation_tree (mqs, parent):
    """Just display the current contents of the J22 object"""
    jsq.show_derivation_tree(trace=True)

def _tdl_job_print_help (mqs, parent):
    """Just display the current contents of the J22 object"""
    jsq.help(trace=True)


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        jsq = Jseq22(stations=range(1,4),
                     solvermenu='solver',
                     # insist=dict(mode='realimag'),
                     inhibit_selection=True)
        jsq.display('initial')

    if 1:
        jsq.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        jsq.grow(ns, test=test, trace=False)

    if 1:
        jsq.display('final', OM=True, full=True)

    if 0:
        jsq.help()



#===============================================================

