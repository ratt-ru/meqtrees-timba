# file: ../Grunt/Vis22.py

# History:
# - 05jan2007: creation (from JEN_SolverChain.py)

# Description:

# The Vis22 class encapsulates a set of 2x2 cohaerency matrices,
# i.e. visbilities. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Matrix22 import *

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

# Global counter used to generate unique node-names
unique = -1


#======================================================================================

class Vis22 (Matrix22):
    """Class that represents a set of 2x2 Cohaerency  matrices"""

    def __init__(self, ns, quals=[], label='<v>',
                 cohset=None, array=None, observation=None,
                 polrep=None,
                 simulate=False):

        # Interface with Meow system (array, cohset, observation):
        self._array = array                          # Meow IfrArray object
        self._observation = observation              # Meow Observation object

        # Initialise its Matrix22 object:
        Matrix22.__init__(self, ns, quals=quals, label=label,
                          polrep=polrep, 
                          indices=self._array.ifrs(),
                          simulate=simulate)
        if cohset:
            self._matrix = cohset
        else:
            quals = self.quals()
            node = self._ns << Meq.Matrix22(complex(1.0),complex(0.0),
                                            complex(0.0),complex(1.0))
            print node
            name = 'init'
            self._matrix = self._ns[name](*quals)
            for ifr in self.ifrs():
                self._matrix(*ifr) << Meq.Identity(node)
                print '-', ifr, self._matrix(*ifr)
            # self.matrix(new=self._ns[name](*quals))

        # List of children to be added to a (solver) reqseq eventually:
        self._reqseq_children = []

        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self.stations()))
        ss += '  quals='+str(self.quals())
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        # print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        return True

    #--------------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        return self._array.stations()                # Meow IfrArray            

    def ifrs (self, select='all'):
        """Get a selection of self._array.ifrs()"""
        return self.indices()                        # Meow IfrArray.ifrs()


    #--------------------------------------------------------------------------

    def append (self, node, quals=None):
        """Append a node to the internal list of reqseq children"""
        if isinstance(node, (list,tuple)):
            self._reqseq_children.extend(node)
        else:
            self._reqseq_children.append(node)
        return True

    def insert_reqseq (self):
        """Make the reqseq node(s) and insert it in the cohset (...).
        The reqseq that executes the solvers in order of creation,
        and then passes on the final residuals (in new cohset)."""
        self.visualize_matrix (tag='reqseq', page='e2e', errorbars=True)
        n = len(self._reqseq_children)
        self._reqseq_children.append(0)               # placeholder 
        cohset = self.cohset()
        for ifr in self.ifrs():
            self._reqseq_children[n] = self._matrix(*ifr)   # fill in the placeholder
            self._ns.reqseq_SolverChain(*ifr) << Meq.ReqSeq(children=self._reqseq_children,
                                                            result_index=n,
                                                            cache_num_active_parents=1)
        if True: self.display('insert_reqseq')
        self._matrix = self._ns.reqseq_SolverChain
        self.make_actual_bookmarks()
        self._clear()                                 # ....??
        return True


    #--------------------------------------------------------------------------
    # Operations on the internal self._matrix:
    #--------------------------------------------------------------------------

    def make_sinks (self, output_col='RESIDUALS', vdm='vdm'):
        """Make sinks for the cohset, and a named VisDataMux"""
        for p,q in self.ifrs():
            self._ns.sink(p,q) << Meq.Sink(self._matrix(p,q),
                                           station_1_index=p-1,
                                           station_2_index=q-1,
                                           output_col=output_col)
        self._ns[vdm] << Meq.VisDataMux(*[self._ns.sink(*ifr) for ifr in self.ifrs()]);
        self._matrix = self._ns.sink           
        return True

    #...........................................................................

    def addnoise (self, rms=0.1):
        """Add gaussian noise with given rms to the internal cohset"""
        quals = self.quals()
        for ifr in self.ifrs():
            rnoise = self._ns.rnoise(*quals)(*ifr) << Meq.GaussNoise(stddev=rms)
            inoise = self._ns.inoise(*quals)(*ifr) << Meq.GaussNoise(stddev=rms)
            noise = self._ns.noise(*quals)(*ifr) << Meq.ToComplex(rnoise,inoise)
            self._ns.addnoise(*quals)(*ifr) << Meq.Add(self._matrix(*ifr),noise)
        self._matrix = self._ns.addnoise(*quals)           
        self._visualize('addnoise')
        return True

    #...........................................................................

    def peel (self, subtract=None):
        """Subtract (peel) a cohset (e.g. a source) from the internal cohset"""
        quals = self.quals()
        for ifr in self.ifrs():
            self._ns.peeled(*quals)(*ifr) << Meq.Subtract(self._matrix(*ifr),
                                                          subtract(*ifr))
        self._matrix = self._ns.peeled(*quals)           
        self._visualize('peel')
        return True

    #...........................................................................

    def unpeel (self, scope=None, add=None):
        """Add (unpeel/restore) a cohset (e.g. a source) to the internal cohset"""
        quals = self.quals(*quals)
        for ifr in self.ifrs():
            unpeel = self._ns << Meq.Stripper(add(*ifr))
            self._ns.unpeeled(*quals)(*ifr) << Meq.Add(self._matrix(*ifr), unpeel)
        self._matrix = self._ns.unpeeled(*quals)              
        self._visualize('unpeel')
        return True

    #...........................................................................

    def corrupt (self, jones=None, rms=0.0, scope=None):
        """Corrupt the internal cohset with the given Jones matrices"""
        quals = self.quals(*quals)
        for ifr in self.ifrs():
            j1 = jones(ifr[0])
            j2c = jones(ifr[1])('conj') ** Meq.ConjTranspose(jones(ifr[1])) 
            self._ns.corrupted(*quals)(*ifr) << Meq.MatrixMultiply(j1,self._matrix(*ifr),j2c)
        self._matrix = self._ns.corrupted(*quals)              
        self._visualize('corrupt')
        if rms>0.0:
            # Optional: add gaussian noise (AFTER corruption, of course):
            self.addnoise(rms)
        return True

    #...........................................................................

    def correct (self, jones=None, scope=None):
        """Correct the internal cohset with the given Jones matrices"""
        quals = self.quals(*quals)
        for ifr in self.ifrs():
            j1i = jones(ifr[0])('inv') ** Meq.MatrixInvert22(jones(ifr[0]))
            j2c = jones(ifr[1])('conj') ** Meq.ConjTranspose(jones(ifr[1])) 
            j2ci = j2c('inv') ** Meq.MatrixInvert22(j2c)
            self._ns.corrected(*quals)(*ifr) << Meq.MatrixMultiply(j1i,self._matrix(*ifr),j2ci)
        self._matrix = self._ns.corrected(*quals)              
        self._visualize('correct')
        return True






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    observation = Meow.Observation(ns)
    allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
    l = 1.0
    m = 1.0
    src = '3c84'
    src_dir = Meow.LMDirection(ns, src, l, m)
    source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
    allsky.add(source)
    cohset = allsky.visibilities(array, observation)
    vis = Vis22(ns, label='test', array=array, cohset=cohset)
    # vis.display()
    cc.append(vis.bundle())

    ns.result << Meq.ReqSeq(children=cc)
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
        import Meow
        num_stations = 3
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
        l = 1.0
        m = 1.0
        src = '3c84'
        src_dir = Meow.LMDirection(ns, src, l, m)
        source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
        allsky.add(source)
        cohset = allsky.visibilities(array, observation)
        vis = Vis22(ns, label='test', array=array, cohset=cohset)
        vis.display()


#=======================================================================
# Remarks:

#=======================================================================
