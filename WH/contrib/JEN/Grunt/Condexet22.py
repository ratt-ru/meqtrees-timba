# file: ../Grunt/Condexet22.py

# History:
# - 18jan2007: creation

# Description:

# The Condexet22 class encapsulates a set of 2x2 condeq matrices. 
# It is derived from the Matrixet22 class.
# It is created with two other Matrixet classes (lhs and rhs)

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
                 lhs=None, rhs=None, wgt=None):

        self._lhs = lhs
        self._rhs = rhs
        self._wgt = wgt

        if rhs:
            quals = lhs.quals(prepend=quals, merge=rhs.quals())
        else:
            quals = lhs.quals(prepend=quals)

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, quals=quals, label=label,
                                       indices=lhs.indices())

        # Placeholder (see .make_condeqs()):
        self._condeqs = []
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
        if self._rhs: print ' * rhs: '+str(self._rhs.oneliner())
        print ' * wgt: '+str(type(self._wgt))
        ii = range(len(self._condeqs))
        print ' * list of condeq nodes ('+str(len(ii))+'):'
        for i in ii:
            print '  - '+str(self._condeqs[i])
        return True


    #--------------------------------------------------------------------------

    def make_condeqs (self, matrel='*', qual=None, unop=None):
        """Make a list of condeq nodes from the internal lhs and rhs Matrixets,
        by comparing the corresponding matrices (or -elements)"""

        quals = self.quals(prepend=unop, append=qual)

        # It is possible to use only a subset of the matrix elements:
        keys = self._matrel.keys()            # i.e. ['m11','m12','m21','m22']
        mel = deepcopy(matrel)
        if mel=='*': mel = keys
        if not isinstance(mel,(list,tuple)): mel = [mel]
        index = []
        postfix = ''
        # self._matrel_index = dict(m11=[0,0], m12=[0,1], m21=[1,0], m22=[1,1])
        for i in range(len(keys)):
            if keys[i] in mel:
                # index.append(i)
                index.append(self._matrel_index[keys[i]])
                postfix += '_'+str(i)
        # index = index[0]
        
        # Allways make condeq nodes for the full 2x2 matrices.
        # These are used for visualisation later
        name = 'condeq'
        i1 = self.list_indices()[0]
        # if not self._ns[name](*quals)(*i1).initialized():           # avoid duplucation
        if True:
            ii = self.list_indices()                                  # selection....?
            indices = []
            for i in ii:
                indices.append(i)
                node1 = self._lhs._matrixet(*i)
                node2 = self._rhs._matrixet(*i)
                if unop:
                    # Optionally, apply a unary operation on both inputs:
                    node1 = self._ns << getattr(Meq, unop)(node1)
                    node2 = self._ns << getattr(Meq, unop)(node2)
                c = self._ns[name](*quals)(*i) << Meq.Condeq(node1, node2)
            self._matrixet = self._ns[name](*quals)
            self.indices(new=indices)

        # Finished: Return a list of condeq nodes:
        return self.make_condeq_nodes (index, postfix, quals, unop=unop)



    #-----------------------------------------------------------------------------

    def make_condeq_nodes (self, index, postfix, quals, unop=None):
        """Helper function called from make_condeqs()"""

        # Make a list of condeq nodes:
        self._condeqs = []
        if (len(index)==4):
            # Use the 2x2 condeq matrices (all 4 matrix elements are used):
            for i in self.list_indices():
                self._condeqs.append(self._matrixet(*i))

        elif False:
            # Make separate condeqs for the subset of required matrix elements:
            # Gives some problems: Use a separate selector per selected corr
            # in Condexet22? Because selector cannot handle index=((0,0),(1,1))
            # nor index=(0,3) if dims=[2,2]............??
            # So, use index=(0,0) and index=(1,1) separately ..........................!!
            name = 'condeq'+postfix
            name1 = 'lhs'+postfix
            name2 = 'rhs'+postfix
            for i in self.list_indices():
                node1 = self._lhs._matrixet(*i)
                node2 = self._rhs._matrixet(*i)
                node1 = self._ns[name1].qadd(node1) << Meq.Selector(node1, index=index)
                node2 = self._ns[name2].qadd(node2) << Meq.Selector(node2, index=index)
                if unop:
                    # Optionally, apply a unary operation on both inputs:
                    node1 = self._ns << getattr(Meq, unop)(node1)
                    node2 = self._ns << getattr(Meq, unop)(node2)
                c = self._ns[name](*quals)(*i) << Meq.Condeq(node1, node2)
                self._condeqs.append(c)

        else:
            # Make separate condeqs for the required matrix elements:
            # (use the Selector for a single matrix element only....)
            for idx in index:
                postfix = str(idx)
                name = 'condeq'+postfix
                name1 = 'lhs'+postfix
                name2 = 'rhs'+postfix
                for i in self.list_indices():
                    node1 = self._lhs._matrixet(*i)
                    node2 = self._rhs._matrixet(*i)
                    node1 = self._ns[name1].qadd(node1) << Meq.Selector(node1, index=idx)
                    node2 = self._ns[name2].qadd(node2) << Meq.Selector(node2, index=idx)
                    if unop:
                        # Optionally, apply a unary operation on both inputs:
                        node1 = self._ns << getattr(Meq, unop)(node1)
                        node2 = self._ns << getattr(Meq, unop)(node2)
                    c = self._ns[name](*quals)(*i) << Meq.Condeq(node1, node2)
                    self._condeqs.append(c)

        # Return the list of condeq nodes:
        return self._condeqs



#======================================================================================
# Version with redundany ()
#======================================================================================

class RedunCondexet22 (Condexet22):
    """Specialized version of the Condexet22 object, without a right-hand side (rhs)
    Visset22 object (predicted data). The MeqCondeq nodes compare redundant spacings,
    rather than measured and predicted data."""

    def __init__(self, ns, quals=[], label='rcdxet', lhs=None, wgt=None, **pp):

        # Make sure the pp (extra parameters) is a dict.
        if not isinstance(pp, dict): pp = dict()
        pp.setdefault('redun', None)
        pp.setdefault('WSRT_9A', 36)

        # Initialise its Condexet22 object:
        Condexet22.__init__(self, ns, quals=quals, label=label, lhs=lhs)

        # Deal with the redundant spacings:
        self._redun = pp['redun']
        self._WSRT_9A = pp['WSRT_9A']            # WSRT separation 9-A (m)
        self._WSRT_xx = None                     # WSRT RT positions
        if self._WSRT_9A:
            self._WSRT_xx = self.get_WSRT_1D_station_pos(self._WSRT_9A)
            self.make_redun_pairs(ifrs=lhs.list_indices())

        return None


    #---------------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  lhs='+str(self._lhs.label())
        ss += '  quals='+str(self.quals())
        if self._WSRT_9A:
            ss += '  WSRT_9A='+str(self._WSRT_9A)+'m'
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print ' * lhs: '+str(self._lhs.oneliner())
        print ' * wgt: '+str(type(self._wgt))
        if self._WSRT_9A:
            print ' * WSRT_xx (m): '+str(self._WSRT_xx)
            print ' * redun: '+str(self._redun)
            print ' * redun_label: '+str(self._redun_label)
        ii = range(len(self._condeqs))
        print ' * list of condeq nodes ('+str(len(ii))+'):'
        for i in ii:
            print '  - '+str(self._condeqs[i])
        return True

    #---------------------------------------------------------------------------

    def get_WSRT_1D_station_pos(self, sep9A=None):
        """Helper function to get 1D WSRT station positions (m), depending on
        separation 9-A (m). Used for redundant-spacing calibration.""" 
        xx = range(14)
        for i in range(10): xx[i] = i*144.0
        xx[10] = xx[9]+sep9A                     # A = 9 + sep9A
        xx[11] = xx[10]+72                       # B = A + 72
        xx[12] = xx[10]+(xx[9]-xx[0])            # C = A + (9-0)
        xx[13] = xx[12]+72                       # D = C + 72
        return xx

    def make_redun_pairs (self, ifrs=None, select='all'):
        """Create a list of redundant pairs of ifrs""" 
        self._redun = []
        self._redun_label = []
        xx = self._WSRT_xx
        for i in range(len(ifrs)-1):
            ifr1 = ifrs[i]
            b1 = xx[ifr1[1]-1] - xx[ifr1[0]-1]            # ifr stations are 1-relative!
            for j in range(i+1,len(ifrs)):
                ifr2 = ifrs[j]
                b2 = xx[ifr2[1]-1] - xx[ifr2[0]-1]        # ifr stations are 1-relative!
                if b2==b1:
                    self._redun.append([ifr1,ifr2])
                    self._redun_label.append(str(int(b1)))
                    break
        return True

    #---------------------------------------------------------------------------

    def make_condeqs (self, matrel='*', qual=None, unop=None):
        """Re-implementation of Condexet22 function make_condeqs().
        Make a list of condeq nodes from the the list of redundant ifr pairs"""

        quals = self.quals(prepend=unop, append=qual)

        # It is possible to use only a subset of the matrix elements:
        keys = self._matrel.keys()            # i.e. ['m11','m12','m21','m22']
        mel = deepcopy(matrel)
        if mel=='*': mel = keys
        if not isinstance(mel,(list,tuple)): mel = [mel]
        index = []
        postfix = ''
        # self._matrel_index = dict(m11=[0,0], m12=[0,1], m21=[1,0], m22=[1,1])
        for i in range(len(keys)):
            if keys[i] in mel:
                # index.append(i)
                index.append(self._matrel_index[keys[i]])
                postfix += '_'+str(i)
        # index = index[0]
        
        # Allways make condeq nodes for the full 2x2 matrices.
        # These are used for visualisation later (if replace=True)
        name = 'redun_condeq'
        i1 = self.list_indices()[0]
        # if not self._ns[name](*quals)(*i1).initialized():          # avoid duplucation
        if True:
            indices = []
            for k,pair in enumerate(self._redun):
                node1 = self._lhs._matrixet(*pair[0])
                node2 = self._lhs._matrixet(*pair[1])
                if unop:
                    # Optionally, apply a unary operation on both inputs:
                    node1 = self._ns << getattr(Meq, unop)(node1)
                    node2 = self._ns << getattr(Meq, unop)(node2)
                ii = list(pair[0])
                ii.extend(pair[1])
                ii.append(self._redun_label[k])
                indices.append(ii)
                self._ns[name](*quals)(*ii) << Meq.Condeq(node1, node2)
            self._matrixet = self._ns[name](*quals)
            self.indices(new=indices)

        # Finished: Return a list of condeq nodes:
        nodes = self.make_condeq_nodes (index, postfix, quals, unop=unop)

        if False:
            # Make the first visibility equal to a unit-matrix, to block the
            # 'solution' in which all visibilities are driven to zero
            pair = self._redun[0]
            firstcoh = self._lhs._matrixet(*pair[0])
            unit_matrix = self._ns['unit_matrix'](*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                                          complex(0.0),complex(1.0))
            
            condeq = self._ns['firstcoh=complex(1)'](*quals) << Meq.Condeq(firstcoh, unit_matrix)
            nodes.append(condeq)

        return nodes




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

    if 1:
        pred = Visset22.Visset22(ns, label='pred', array=array)
        pred.fill_with_identical_matrices()
        pred.display()

        if 1:
            cdx = Condexet22(ns, lhs=data, rhs=pred)
            cdx.display(recurse=2)

            if 1:
                cdx.make_condeqs()
                cdx.visualize()
                cdx.display(recurse=2)

            if 0:
                cdx.make_condeqs(unop='Abs')
                cdx.display(recurse=2)

            if 0:
                cdx.make_condeqs(matrel=['m12','m22'], unop='Abs')
                cdx.display(recurse=2)

    if 1:
        cdr = RedunCondexet22(ns, lhs=data)
        cdr.display(recurse=2)

        if 1:
            cdr.make_condeqs()
            cdr.display(recurse=2)
            cdr.visualize()



#=======================================================================
# Remarks:

#=======================================================================
