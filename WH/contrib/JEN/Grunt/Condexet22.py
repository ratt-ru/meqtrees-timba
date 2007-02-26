# file: ../Grunt/Condexet22.py

# History:
# - 18jan2007: creation
# - 23feb2007: second iteration

# Description:

# The Condexet22 class encapsulates a set of 2x2 condeq matrices.
# It is derived from the Matrixet22 class.
# It is created with at least one other Matrixet class (lhs), which
# provides the left-hand-side children of the condeqs.
# - If a right-hand-side (rhs) Matrixet22 is supplied, it provides the
#   second children of the condeqs. It is assumed that both Matrixets
#   have the same indices (i.e. ifrs, or stations). It is possible to
#   select the matrices from which condeqs are made (default is all).
# - If no rhs is supplied (rhs=None), the matrices of the lhs are
#   compared with each other. A 'redun' dict specifies which matrices
#   are expected to be equal ('redundant'), and to what. The latter
#   can be a constant, or a parametrized expression. So, the Condexet22
#   has a ParmGroupManager (pgm) attribute.
# With these two modes, it is possible to feed a mixture of selfcal
# and redundancy equations to a solver (with appropriate weights).

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Matrixet22

from copy import deepcopy

# For testing only:
import Meow
# from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.Grunt import Visset22


Settings.forest_state.cache_policy = 100

# Global counter used to generate unique node-names
# unique = -1

        
#======================================================================================

class Condexet22 (Matrixet22.Matrixet22):
    """Class that represents a set of 2x2 matrices of MeqCondeq nodes,
    which generate condition equations for a MeqSolver node. The left-hand
    side (lhs) is a Visset22 object with measured data, while the right-hand
    side (rhs) contains predicted visibilities."""

    def __init__(self, ns, quals=[], label='cdxet',
                 lhs=None, wgt=None, select='*'):

        self._lhs = lhs
        self._wgt = wgt
        self._select = select

        # Placeholders:
        self._rhs = None
        self._redun = None

        self._condeq_name = 'condeq'

        # Initialise its Matrixet22 object:
        quals = lhs.quals(prepend=quals)
        Matrixet22.Matrixet22.__init__(self, ns, quals=quals, label=label)

        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  lhs='+str(self._lhs.label())
        if self._rhs: ss += '  rhs='+str(self._rhs.label())
        ss += '  quals='+str(self.quals())
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print ' * lhs: '+str(self._lhs.oneliner())
        print ' * select: '+str(self._select)
        if self._rhs:
            print ' * rhs: '+str(self._rhs.oneliner())
        if self._redun:
            print ' * redun: '
            for key in self._redun.keys():
                print '  - '+str(key)+': '
        print ' * wgt: '+str(type(self._wgt))
        nodes = self.get_condeqs(matrel='*')
        print ' * list of condeq nodes ('+str(len(nodes))+'):'
        for k,node in enumerate(nodes):
            print '  - '+str(k)+': '+str(node) 
        return True

    #-----------------------------------------------------------------------------

    def get_condeqs (self, matrel='*'):
        """Get a list of the condeq nodes defined with make_condeqs() etc."""
        nodes = []
        if matrel=='*':
            for i in self.list_indices():
                nodes.append(self._matrixet(*i))
        else:
            nodes = self.extract_matrix_element(matrel)
        return nodes
        

    #--------------------------------------------------------------------------

    def make_condeqs (self, rhs=None, unop=None):
        """Make condeq matrices by equating the corresponding matrices 
        of the internal lhs, and the given rhs Matrixet22 objects.
        Optionally, apply an unary operation to both sides before equating."""

        self._rhs = rhs
        quals = self.quals()
        indices = self.indices()
        ii = self._lhs.list_indices()                             # selection....?
        name = self._condeq_name
        for i in ii:
            indices.append(i)
            node1 = self._lhs._matrixet(*i)
            node2 = self._rhs._matrixet(*i)
            if unop:
                # Optionally, apply a unary operation on both inputs:
                node1 = self._ns << getattr(Meq, unop)(node1)
                node2 = self._ns << getattr(Meq, unop)(node2)
            self._ns[name](*quals)(*i) << Meq.Condeq(node1, node2)
        self._matrixet = self._ns[name](*quals)
        self.indices(new=indices)
        return True


    #------------------------------------------------------------------
    
    def make_redun_condeqs (self, rr, unop=None):
        """Make condeq matrices by equating pairs of matrices that represent
        equal (redundant) baselines in the internal lhs Matrixet22 object.
        The pairs of ifr-indices, and their identifying labels, are specified
        as lists (in fields named 'pairs' and 'labels') in the given dict rr. 
        Optionally, apply an unary operation to both sides before equating."""

        quals = self.quals()
        name = self._condeq_name
        indices = self.indices()
        for k,pair in enumerate(rr['pairs']):
            node1 = self._lhs._matrixet(*pair[0])
            node2 = self._lhs._matrixet(*pair[1])
            if unop:
                # Optionally, apply a unary operation on both inputs:
                node1 = self._ns << getattr(Meq, unop)(node1)
                node2 = self._ns << getattr(Meq, unop)(node2)
            # The new matrixet index has 5 parts: 
            index = list(pair[0])             # the 2 stations of ifr1          
            index.extend(pair[1])             # the 2 stations of ifr2
            index.append(rr['labels'][k])     # the label (baseline length)
            indices.append(index)
            self._ns[name](*quals)(*index) << Meq.Condeq(node1, node2)
        self._matrixet = self._ns[name](*quals)
        self.indices(new=indices)
        return True


    #------------------------------------------------------------------
    
    def make_group_condeqs (self, rr, corrupt=None, unop=None):
        """Make condeq matrices by equating groups of matrices that represent
        equal (redundant) baselines in the internal lhs Matrixet22 object
        to the same node, which can be either a constant or a MeqParm.
        In the last case, it should be solved for, using the ParmGroupManager.
        The groups (of ifr-indices) and other info, are specified as named dicts
        in the given dict rr. Each group dict has fields 'group' (list of ifrs)
        and 'rhs' (which specifies what the group is equated to. The rhs field
        may be either 'constant', 'diagonal', or 'allfour'.
        Optionally, apply an unary operation to both sides before equating."""

        quals = self.quals()
        name = self._condeq_name
        indices = self.indices()
        for key in rr.keys():
            # Make the (matrix) node that the redundant matrices are equated to:
            node2 = self.make_group_node2 (rr[key], key=key, quals=quals)
            # Make condeqs that equate the group members to node2
            for ifr in rr[key]['group']:
                node1 = self._lhs._matrixet(*ifr)
                if unop:
                    # Optionally, apply a unary operation on both inputs:
                    node1 = self._ns << getattr(Meq, unop)(node1)
                    node2 = self._ns << getattr(Meq, unop)(node2)
                # The new matrixet index has 3 parts: 
                index = list(ifr)                      # the 2 stations of ifr
                index.append(key)                      # the key (baseline length)
                indices.append(index)
                self._ns[name](*quals)(*index) << Meq.Condeq(node1, node2)
        self._matrixet = self._ns[name](*quals)
        self.indices(new=indices)
        return True


    #.............................................................................

    def make_group_node2 (self, rr, key, quals=None):
        """Helper function for .make_group_condeqs()"""

        rhs = rr['rhs']

        if not isinstance(rhs, str):
            # Assume that rhs is a node already:
            return rhs
        
        elif rhs=='constant':
            name = 'unit_matrix'
            return self._ns[name](*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                          complex(0.0),complex(1.0))

        # The following possibilities all require MeqParms:

        self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                              default=dict(c00=0.0, unit='rad', tfdeg=[0,0],
                                           subtile_size=1),
                              constraint=dict(sum=0.0, first=0.0),
                              simul=dict(Psec=200),
                              override=override,
                              rider=dict(matrel=matrel),
                              tags=[pname,jname])

        elif rhs=='diagonal':
            name = 'diag_parms'
            node2 = self._ns[name](*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                           complex(0.0),complex(1.0))
        else:
            name = 'full_parms'
            node2 = self._ns[name](*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                           complex(0.0),complex(1.0))
        return node2





#======================================================================================
#======================================================================================
#======================================================================================
# Stand-alone helper routines:
#======================================================================================

def get_WSRT_1D_station_pos(sep9A=36):
    """Helper function to get 1D WSRT station positions (m), depending on
    separation 9-A (m). Used for redundant-spacing calibration.""" 
    xx = range(14)
    for i in range(10): xx[i] = i*144.0
    xx[10] = xx[9]+sep9A                     # A = 9 + sep9A
    xx[11] = xx[10]+72                       # B = A + 72
    xx[12] = xx[10]+(xx[9]-xx[0])            # C = A + (9-0)
    xx[13] = xx[12]+72                       # D = C + 72
    return xx

#-------------------------------------------------------------------------------------

def make_WSRT_redun_pairs (ifrs=None, sep9A=36, select='all'):
    """Create a list of redundant pairs of WSRT ifrs""" 
    rr = dict(pairs=[], labels=[])
    xx = get_WSRT_1D_station_pos(sep9A=sep9A)
    for i in range(len(ifrs)-1):
        ifr1 = ifrs[i]
        b1 = xx[ifr1[1]-1] - xx[ifr1[0]-1]            # ifr stations are 1-relative!
        for j in range(i+1,len(ifrs)):
            ifr2 = ifrs[j]
            b2 = xx[ifr2[1]-1] - xx[ifr2[0]-1]        # ifr stations are 1-relative!
            if b2==b1:
                rr['pairs'].append([ifr1,ifr2])
                rr['labels'].append(str(int(b1)))
                break
    return rr

#-------------------------------------------------------------------------------------

def make_WSRT_redun_groups (ifrs=None, sep9A=36, select='all'):
    """Create a dict of named groups of redundant WSRT ifrs""" 

    # Make named (key) groups of baselines with the same length: 
    rr = dict()
    xx = get_WSRT_1D_station_pos(sep9A=sep9A)
    for i in range(len(ifrs)):
        ifr = ifrs[i]
        b = xx[ifr[1]-1] - xx[ifr[0]-1]               # ifr stations are 1-relative!
        key = str(int(b))
        rr.setdefault(key, dict(group=[], rhs='diagonal'))
        rr[key]['group'].append(ifr)

    # Remove the groups with only a single member:
    # print dir(rr)
    for key in rr.keys():
        print '-',key,':',rr[key],
        if len(rr[key]['group'])==1:
            rr.__delitem__(key)
            print 'removed'
        else:
            print
    return rr








#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    num_stations = 5
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    # observation = Meow.Observation(ns)
    data = Visset22.Visset22(ns, label='data', array=array)
    data.fill_with_identical_matrices(stddev=0.01)
    cc.append(data.visualize())
    data.display()

    unop=None
    unop='Abs'
    matrel = '*'
    # matrel = 'm11'

    if True:
        pred = Visset22.Visset22(ns, label='pred', array=array)
        pred.fill_with_identical_matrices(stddev=0.1)
        pred.display()
        cc.append(pred.visualize())
        cdx = Condexet22(ns, lhs=data, rhs=pred)
        cdx.make_condeqs(matrel=matrel, unop=unop)
        cc.append(cdx.visualize())
        cdx.display()
        cc.append(cdx.bundle())

    if False:
        cdr = RedunCondexet22(ns, lhs=data)
        cdr.display(recurse=2)
        cdr.make_condeqs(matrel=matrel, unop=unop)
        cc.append(cdr.visualize())
        cdr.display()
        cc.append(cdr.bundle())
    
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
       



#=======================================================================
# Test program (standalone):
#=======================================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        num_stations = 5
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        # observation = Meow.Observation(ns)
        data = Visset22.Visset22(ns, label='data', array=array)
        data.fill_with_identical_matrices()
        data.display()
        cdx = Condexet22(ns, lhs=data)
        cdx.display(recurse=2)

    if 0:
        rr = make_WSRT_redun_pairs (ifrs=array.ifrs(), sep9A=36, select='all')
        cdx.make_redun_condeqs (rr, unop=None)
        cdx.display(recurse=3)

    if 1:
        rr = make_WSRT_redun_groups (ifrs=array.ifrs(), sep9A=36, select='all')
        cdx.make_group_condeqs (rr, unop=None)
        cdx.display(recurse=4)

    if 0:
        pred = Visset22.Visset22(ns, label='pred', array=array)
        pred.fill_with_identical_matrices()
        pred.display()
        cdx.make_condeqs(rhs=pred, unop='Abs')
        # cdx.visualize()
        cdx.display(recurse=3)

    if 0:
        matrel = 'm12' 
        print '\n** get_condeqs(',matrel,'):'
        nodes = cdx.get_condeqs(matrel=matrel)
        for k,node in enumerate(nodes):
            print k,':',node 
        print

#=======================================================================
# Remarks:

#=======================================================================
