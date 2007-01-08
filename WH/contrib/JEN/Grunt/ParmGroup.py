# file: ../Grunt/ParmGroup.py

# History:
# - 25dec2006: creation
# - 03jan2007: re-implemented as a specialization of class NodeGroup
# - 03jan2007: created another specialization class SimulatedParmGroup 

# Description:

# The ParmGroup class encapsulates a named group of MeqParm nodes,
# or subtrees that generate simulated values for MeqParm nodes.
# ParmGroups are created in modules that implement bits of a
# Measurement Equation that contain parameters, e.g. instrumental
# Jones matrices, or LSM source models. They may be used for
# solving or visualization. They are also useful for generating
# user interfaces that offer a choice of solvers, etc.

#==========================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import NodeGroup 

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy
import random
import math



#==========================================================================

class ParmGroup (NodeGroup.NodeGroup):
    """Class that represents a group of (somehow related) MeqParm nodes"""

    def __init__(self, ns, label='<pg>', nodelist=[],
                 quals=[], descr=None, tags=[], node_groups=[],
                 color='blue', style='circle', size=8, pen=2,
                 default=0.0, 
                 rider=None):

        NodeGroup.NodeGroup.__init__(self, ns=ns, label=label, nodelist=nodelist,
                                     quals=quals, descr=descr, tags=tags, 
                                     color=color, style=style, size=size, pen=pen,
                                     rider=rider)

        # Information needed to create MeqParm nodes (see create_entry())
        self._default = default               # default value
        self._node_groups = deepcopy(node_groups)
        if not isinstance(self._node_groups,(list,tuple)):
            self._node_groups = [self._node_groups]
        if not 'Parm' in self._node_groups:
            self._node_groups.append('Parm')

        return None
                
    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - default: '+str(self._default)
        print '   - node_groups: '+str(self._node_groups)
        return True

    #-------------------------------------------------------------------

    def create_entry (self, qual=None):
        """Create an entry, i.e. MeqParm node, or a simulation subtree,
        and append it to the nodelist"""

        # If in a qualifier (qual) is specified, append it to the temporary quals list: 
        quals = self._quals.get(append=qual)
            
        node = self._ns.parm(*quals) << Meq.Parm(self._default,
                                                 node_groups=self._node_groups,
                                                 tags=self._tags)
        # Append the new node to the internal nodelist:
        self.append_entry(node)
        return node


    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""
        self.create_entry()
        self.create_entry(5)
        self.create_entry(6)
        return True








#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================


class SimulatedParmGroup (NodeGroup.NodeGroup):
    """Class that represents a group of nodes (subtrees) that simulate
    a group of MeqParm nodes (often used in conjunction with class ParmGroup)"""

    def __init__(self, ns, label='<pg>', nodelist=[],
                 quals=[], descr=None, tags=[], node_groups=[],
                 color='blue', style='circle', size=8, pen=2,
                 default=0.0, ctrl=None, rider=None):

        NodeGroup.NodeGroup.__init__(self, ns=ns, label=label, nodelist=nodelist,
                                     quals=quals, descr=descr, tags=tags, 
                                     color=color, style=style, size=size, pen=pen,
                                     rider=rider)

        # Make sure that tags/quals of the created nodes reflect the fact
        # that this is a simulated parameter.
        self._tags.append('simul')            # ....??
        self._quals.append('simul')

        # The default value of the MeqParm that is being simulated:
        self._default = default               # default value

        # Information to create a simulation subtree (see create_entry())
        pp = dict()                           # Simulation control info
        if isinstance (ctrl, dict):
            pp = deepcopy(ctrl)
        pp.setdefault('scale', None)
        pp.setdefault('stddev', 0.1)          # stddev of default value (relative!) 
        pp.setdefault('Tsec', 1000.0)         # Time variation (cos) period
        pp.setdefault('Tstddev', 0.1)         # stddev of Tsec (relative!)

        # Some checks:
        if pp['scale']==None:
            pp['scale'] = abs(self._default)  #   use the (non-zero!) default value
            if pp['scale']==0.0: pp['scale'] = 1.0

        # Store:
        self._ctrl = pp 
        return None
                
    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - default: '+str(self._default)
        for key in self._ctrl.keys():
            print '   - '+key+' = '+str(self._ctrl[key])
        return True


    #-------------------------------------------------------------------

    def create_entry (self, qual=None):
        """Create an entry, i.e. a simulation subtree, that simulates
        a MeqParm node that varies with time and/or frequency, and append
        it to the nodelist"""

        # If in a qualifier (qual) is specified, append it to the temporary quals list: 
        quals = self._quals.get(append=qual)

        pp = self._ctrl                                 # Convenience
            
        # Expression used:
        #  default += ampl*cos(2pi*time/Tsec),
        #  where both ampl and Tsec may vary from node to node.

        ampl = 0.0
        if pp['stddev']:                                # default variation
            stddev = pp['stddev']*pp['scale']           # NB: pp['stddev is relative
            ampl = random.gauss(ampl, stddev)
        ampl = self._ns.ampl(*quals) << Meq.Constant(ampl)
        
        Tsec = pp['Tsec']                               # variation period (sec)
        if pp['Tstddev']:
            stddev = pp['Tstddev']*pp['Tsec']           # NB: pp['Tstddev is relative
            Tsec = random.gauss(pp['Tsec'], stddev) 
        Tsec = self._ns.Tsec(*quals) << Meq.Constant(Tsec)
        time = self._ns << Meq.Time()
        pi2 = 2*math.pi
        costime = self._ns << Meq.Cos(pi2*time/Tsec)
        variation = self._ns.variation(*quals) << Meq.Multiply(ampl,costime)

        # Finally, add the variation to the default value:
        default = self._ns.default(*quals) << Meq.Constant(self._default)
        node = self._ns.parm(*quals) << Meq.Add(default, variation, tags=self._tags)

        # Append the new node to the internal nodelist:
        self.append_entry(node)
        return node



    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""
        self.create_entry()
        self.create_entry(5)
        self.create_entry(6)
        return True







#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    pg1 = ParmGroup(ns, 'pg1', rider=dict(matrel='m21'))
    pg1.test()
    cc.append(pg1.visualize())
    nn1 = pg1.nodelist()
    print 'nn1 =',nn1

    pg2 = SimulatedParmGroup(ns, 'pg2')
    pg2.test()
    cc.append(pg2.visualize())
    nn2 = pg2.nodelist()
    print 'nn2 =',nn2

    condeqs = []
    for i in range(len(nn1)):
        print '- i =',i
        condeqs.append(ns.condeq(i) << Meq.Condeq(nn1[i],nn2[i]))
    solver = ns.solver << Meq.Solver(children=condeqs, solvable=nn1)
    JEN_bookmarks.create(solver, page='solver')
    cc.append(solver)
        



    ns.result << Meq.Composer(children=cc)
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

    if 0:
        pg1 = ParmGroup(ns, 'pg1', rider=dict(matrel='m21'))
        pg1.test()
        pg1.display()

        if 0:
            dcoll = pg1.visualize()
            pg1.display_subtree (dcoll, txt='dcoll')

    if 1:
        ctrl = dict(Tsec=500)
        pg2 = SimulatedParmGroup(ns, 'pg2', ctrl=ctrl)
        pg2.test()
        pg2.display()



#===============================================================
    
