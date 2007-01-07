# file: ../Grunt/Visset22.py

# History:
# - 05jan2007: creation (from JEN_SolverChain.py)

# Description:

# The Visset22 class encapsulates a set of 2x2 cohaerency matrices,
# i.e. visbilities. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Matrixet22 import *

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

# For testing only:
import Meow
import Joneset22



# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

class Visset22 (Matrixet22):
    """Class that represents a set of 2x2 Cohaerency  matrices"""

    def __init__(self, ns, quals=[], label='<v>',
                 cohset=None, array=None, observation=None,
                 polrep=None,
                 simulate=False):

        # Interface with Meow system (array, cohset, observation):
        self._array = array                          # Meow IfrArray object
        self._observation = observation              # Meow Observation object

        # Initialise its Matrixet22 object:
        Matrixet22.__init__(self, ns, quals=quals, label=label,
                            polrep=polrep, 
                            indices=self._array.ifrs(),
                            simulate=simulate)
        if cohset:
            self._matrixet = cohset
        else:
            quals = self.quals()
            node = self._ns.unity(*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                          complex(0.0),complex(1.0))
            self._matrixet = self._ns.initial(*quals)
            for ifr in self.ifrs():
                self._matrixet(*ifr) << Meq.Identity(node)

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
            self._reqseq_children[n] = self._matrixet(*ifr)   # fill in the placeholder
            self._ns.reqseq_SolverChain(*ifr) << Meq.ReqSeq(children=self._reqseq_children,
                                                            result_index=n,
                                                            cache_num_active_parents=1)
        if True: self.display('insert_reqseq')
        self._matrixet = self._ns.reqseq_SolverChain
        self.make_actual_bookmarks()
        self._clear()                                 # ....??
        return True


    #--------------------------------------------------------------------------
    # Operations on the internal self._matrixet:
    #--------------------------------------------------------------------------

    def make_sinks (self, output_col='RESIDUALS', vdm='vdm'):
        """Make sinks for the cohset, and a named VisDataMux"""
        for p,q in self.ifrs():
            self._ns.sink(p,q) << Meq.Sink(self._matrixet(p,q),
                                           station_1_index=p-1,
                                           station_2_index=q-1,
                                           output_col=output_col)
        self._ns[vdm] << Meq.VisDataMux(*[self._ns.sink(*ifr) for ifr in self.ifrs()]);
        self._matrixet = self._ns.sink           
        return True

    #...........................................................................

    def addNoise (self, rms=0.1, qual=None, visu=True):
        """Add gaussian noise with given rms to the internal cohset"""
        quals = self.quals(append=qual)
        name = 'addNoise22'
        matrels = self.matrels()
        for ifr in self.ifrs():
            mm = range(4)
            for i in range(4):
                m = matrels[i]
                rnoise = self._ns.rnoise(*quals)(*ifr)(m) << Meq.GaussNoise(stddev=rms)
                inoise = self._ns.inoise(*quals)(*ifr)(m) << Meq.GaussNoise(stddev=rms)
                mm[i] = self._ns.noise(*quals)(*ifr)(m) << Meq.ToComplex(rnoise,inoise)
            noise = self._ns.noise(*quals)(*ifr) << Meq.Matrix22(*mm)
            self._ns[name](*quals)(*ifr) << Meq.Add(self._matrixet(*ifr),noise)
        self._matrixet = self._ns[name](*quals)           
        if visu: return self.visualize(name)
        return True

    #...........................................................................

    def corrupt (self, joneset=None, rms=0.0, qual=None, visu=False):
        """Corrupt the internal cohset with the given Jones matrices"""
        quals = self.quals(append=qual)
        name = 'corrupt22'
        for ifr in self.ifrs():
            j1 = joneset(ifr[0])
            j2c = joneset(ifr[1])('conj') ** Meq.ConjTranspose(joneset(ifr[1])) 
            self._ns[name](*quals)(*ifr) << Meq.MatrixMultiply(j1,self._matrixet(*ifr),j2c)
        self._matrixet = self._ns[name](*quals)              
        self._pgm.merge(joneset._pgm)
        if rms>0.0:
            # Optional: add gaussian noise (AFTER corruption, of course):
            self.addNoise(rms)
        if visu: return self.visualize(name)
        return True

    #...........................................................................

    def correct (self, joneset=None, qual=None, visu=False):
        """Correct the internal cohset with the given Jones matrices"""
        quals = self.quals(append=qual)
        name = 'correct22'
        for ifr in self.ifrs():
            j1i = joneset(ifr[0])('inv') ** Meq.MatrixInvert22(joneset(ifr[0]))
            j2c = joneset(ifr[1])('conj') ** Meq.ConjTranspose(joneset(ifr[1])) 
            j2ci = j2c('inv') ** Meq.MatrixInvert22(j2c)
            self._ns[name](*quals)(*ifr) << Meq.MatrixMultiply(j1i,self._matrixet(*ifr),j2ci)
        self._matrixet = self._ns[name](*quals)              
        if visu: return self.visualize(name)
        return True






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)

    cohset = None
    if False:
        observation = Meow.Observation(ns)
        allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
        l = 1.0
        m = 1.0
        src = '3c84'
        src_dir = Meow.LMDirection(ns, src, l, m)
        source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
        allsky.add(source)
        cohset = allsky.visibilities(array, observation)
    vis = Visset22(ns, label='test', quals='yyc', array=array, cohset=cohset)
    vis.display('initial')

    if True:
        G = Joneset22.GJones(ns, stations=array.stations(), simulate=True)
        D = Joneset22.DJones(ns, stations=array.stations(), simulate=True)
        jones = G
        jones = D
        jones = Joneset22.Joneseq22([G,D])
        cc.append(vis.corrupt(jones.matrixet(), visu=True))
        cc.append(vis.addNoise(rms=0.05, visu=True))
        vis.display('after corruption')
        if False:
            cc.append(vis.correct(jones.matrixet(), visu=True))

    if True:
        pred = Visset22(ns, label='nominal', quals='xxc', array=array, cohset=cohset)
        pred.display('initial')
        G = Joneset22.GJones(ns, stations=array.stations(), simulate=False)
        D = Joneset22.DJones(ns, stations=array.stations(), simulate=False)
        jones = G
        jones = D
        jones = Joneset22.Joneseq22([G,D])
        cc.append(pred.corrupt(jones.matrixet(), visu=True))
        vis.display('after corruption')
        cc.append(vis.make_solver(pred))
        if False:
            cc.append(vis.correct(jones.matrixet(), visu=True))
  
    # vis.display('final')
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
        cohset = None
        if False:
            allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
            l = 1.0
            m = 1.0
            src = '3c84'
            src_dir = Meow.LMDirection(ns, src, l, m)
            source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
            allsky.add(source)
            cohset = allsky.visibilities(array, observation)
        vis = Visset22(ns, label='test', array=array, cohset=cohset)
        vis.display()

    if 0:
        G = Joneset22.GJones (ns, stations=array.stations(), simulate=True)
        vis.corrupt(G.matrixet(), visu=True)
        vis.addNoise(rms=0.05, visu=True)
        vis.correct(G.matrixet(), visu=True)
        vis.display('after corruption')

    if 1:
        G = Joneset22.GJones (ns, stations=array.stations(), simulate=True)
        D = Joneset22.DJones (ns, stations=array.stations(), simulate=True)
        jones = Joneset22.Joneseq22([G,D])
        vis.corrupt(jones.matrixet(), visu=True)
        vis.display('after corruption')


#=======================================================================
# Remarks:

#=======================================================================
