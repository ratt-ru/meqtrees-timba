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

# from Timba.Contrib.JEN.util import JEN_bookmarks
# from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

# For testing only:
# import Meow
# from Timba.Contrib.JEN.Grunt import Joneset22



# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

class Condexet22 (Matrixet22.Matrixet22):
    """Class that represents a set of 2x2 Cohaerency  matrices"""

    def __init__(self, ns, quals=[], label=None,
                 lhs=None, rhs=None, wgt=None):

        if label==None: label = 'cdx'
        self._lhs = lhs
        self._rhs = rhs
        self._wgt = wgt
        quals = lhs.quals(prepend=quals, merge=rhs.quals())

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
        ss += '  rhs='+str(self._rhs.label())
        ss += '  quals='+str(self.quals())
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print ' * lhs: '+str(self._lhs.oneliner())
        print ' * rhs: '+str(self._rhs.oneliner())
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
        # These are used for visualisation later (if replace=True)
        name = 'condeq'
        i1 = self.list_indices()[0]
        # if not self._ns[name](*quals)(*i1).initialized():           # avoid duplucation
        if True:
            for i in self.list_indices():
                node1 = self._lhs._matrixet(*i)
                node2 = self._rhs._matrixet(*i)
                if unop:
                    # Optionally, apply a unary operation on both inputs:
                    node1 = self._ns << getattr(Meq, unop)(node1)
                    node2 = self._ns << getattr(Meq, unop)(node2)
                c = self._ns[name](*quals)(*i) << Meq.Condeq(node1, node2)
            self._matrixet = self._ns[name](*quals)


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




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    m1 = Matrixet22.Matrixet22(ns, quals=['3c84','xxx'], label='HH', simulate=True)
    m2 = Matrixet22.Matrixet22(ns, quals=['yyy'], label='GG')
    cdx = Condexet22(ns, lhs=m1, rhs=m2)
    cdx.display()
    
    cc.append(cdx.bundle())
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
        m1 = Matrixet22.Matrixet22(ns, quals=['3c84','xxx'], label='HH', simulate=True)
        m1.test()
        m1.display()
        m2 = Matrixet22.Matrixet22(ns, quals=['yyy'], label='GG')
        m2.test()
        m2.display()
        cdx = Condexet22(ns, lhs=m1, rhs=m2)
        cdx.display(recurse=2)

    if 1:
        cdx.make_condeqs()
        cdx.display(recurse=2)

    if 1:
        cdx.make_condeqs(unop='Abs')
        cdx.display(recurse=2)

    if 1:
        cdx.make_condeqs(matrel=['m12','m22'], unop='Abs')
        cdx.display(recurse=2)



#=======================================================================
# Remarks:

#=======================================================================
