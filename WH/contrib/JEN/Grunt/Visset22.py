# file: ../Grunt/Visset22.py

# History:
# - 05jan2007: creation (from JEN_SolverChain.py)

# Description:

# The Visset22 class encapsulates a set of 2x2 cohaerency matrices,
# i.e. visbilities. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Matrixet22

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

# For testing only:
import Meow
from Timba.Contrib.JEN.Grunt import Joneset22



# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

class Visset22 (Matrixet22.Matrixet22):
    """Class that represents a set of 2x2 Cohaerency  matrices"""

    def __init__(self, ns, quals=[], label='<v>',
                 cohset=None, array=None,
                 observation=None,
                 polrep=None,
                 simulate=False):

        # Interface with Meow system (array, cohset, observation):
        self._array = array                          # Meow IfrArray object
        self._observation = observation              # Meow Observation object

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, quals=quals, label=label,
                                       polrep=polrep, 
                                       indices=self._array.ifrs(),
                                       simulate=simulate)
        if cohset:
            self._matrixet = cohset

        # Some specific Visset22 attributes:
        self._MS_corr_index = [0,1,2,3]                # see make_spigots/make_sinks

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
        print '   - MS_corr_index: '+str(self._MS_corr_index)
        return True

    #--------------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        return self._array.stations()                # Meow IfrArray            

    def ifrs (self, select='all'):
        """Get a selection of self._array.ifrs()"""
        ifrs = self._array.ifrs()                    # Meow IfrArray            
        # ifrs = self.indices()                        # = Meow IfrArray.ifrs()
        # .... do the selection ....
        return ifrs

    #--------------------------------------------------------------------------
    # Operations on the internal self._matrixet:
    #--------------------------------------------------------------------------

    def make_spigots (self, input_col='DATA',
                      MS_corr_index=[0,1,2,3], flag_bit=4,
                      visu=True):
        """Make MeqSpigot nodes per ifr, for reading visibility data from the
        specified 'tile' columns of the VisTile interface.
        Note that tile columns are NOT the same as MS columns! If relevant,
        the latter are specified in the request.
        - The (tile) input_col can be 'DATA','PREDICT','RESIDUALS' (and 'FLAGS'?)
        However, only the 'DATA' column can be populated at this time...(!)
        - Sometimes, not all 4 corrs are available. For XX/YY only, use:
          - If only XX/YY available: MS_corr_index = [0,-1,-1,1]
          - If all 4 corr available: MS_corr_index = [0,-1,-1,3]
          - etc
        For missing corrs, the spigot still returns a 2x2 tensor node, but with
        empty results {}. These are interpreted as zeroes, e.g. in matrix
        multiplication. After that, the results ar no longer empty, so that cannot
        be used for detecting missing corrs! Empty results are ignored by condeqs etc
        See also the wiki-pages...
        """

        self._MS_corr_index = MS_corr_index    # Keep. See also .make_sinks()

        name = 'spigot'
        for p,q in self.ifrs():
            self._ns[name](p,q) << Meq.Spigot(station_1_index=p-1,
                                               station_2_index=q-1,
                                               # corr_index=self._MS_corr_index,
                                               # flag_bit=flag_bit,
                                               input_column=input_col)
        self._matrixet = self._ns[name]

        if False:
            # Optional: insert a dummy node after the spigot for testing
            name = 'dummy'
            for p,q in self.ifrs():
                self._ns[name](p,q) << Meq.Identity(self._matrixet(p,q))
            self._matrixet = self._ns[name]


        # self.create_ReadVisHeader_placeholders()    # see below....

        if visu:
            self.visualize('spigots')
        return True

    #--------------------------------------------------------------------------

    def create_ReadVisHeader_placeholders(self):
        """Create placeholder nodes expected by ReadVisHeader.py"""
        # nodes for phase center
        self._ns.radec0 = Meq.Composer(self._ns.ra<<0, self._ns.dec<<0)
        
        # nodes for array reference position
        self._ns.xyz0 = Meq.Composer(self._ns.x0<<0,
                                     self._ns.y0<<0,
                                     self._ns.z0<<0)
        
        # now define per-station stuff: XYZs and UVWs 
        for p in ANTENNAS:
            self._ns.xyz(p) << Meq.Composer(self._ns.x(p)<<0,
                                            self._ns.y(p)<<0,
                                            self._ns.z(p)<<0)
            self._ns.uvw(p) << Meq.UVW(radec=self._ns.radec0,
                                       xyz_0=self.ns.xyz0,
                                       xyz=self._ns.xyz(p))

        return True

    #--------------------------------------------------------------------------

    def make_sinks (self, output_col='DATA',
                    # start=None, pre=None, post=None,
                    vdm='vdm'):
        """Make MeqSink nodes per ifr for writing visibilities back to the
        specified 'tile' column of the VisTile interface, which conveys it
        to a Measurement Set (MS) or other data-source.
        Note that tile columns are NOT the same as MS columns! If relevant,
        the latter are specified in the request.
        These are the children of a single VisDataMux node, which issues the
        series of requests that traverse the data.
        - Alternatives for the (tile) output_col are 'RESIDUALS','PREDICT','DATA'.
        However, only the 'DATA' column can be populated at this time...(!)
        - The keyword vdm (default='vdm') supplies the name of the VisDataMux node,
        which is needed for executing the tree. It has three optional children:
          - child 'start' gets a request before the spigots are filled
          - child 'pre' gets a request before the MeqSinks
            (may be used to attach a MeqSolver, or its MeqReqSeq)
          - child 'post' gets a request after the MeqSinks have returned a result 
            (may be used to attach all MeqDataCollect nodes)
        """

        # First attach any nodes collected in the 'accumulist' to a ReqSeq,
        # which is then inserted in the matrixet main stream (i.e. all ifrs).
        # The collected nodes are usually solver nodes or dataCollect nodes.
        # The ReqSeq will execute them in that order before executing the current
        # main-stream matrix node. The result of the latter is the only one
        # that is transmitted by the ReqSeq. The accumulist is cleared.
        self.insert_accumulist_reqseq()

        # Make the sinks:
        name = 'sink'
        for p,q in self.ifrs():
            self._ns[name](p,q) << Meq.Sink(self._matrixet(p,q),
                                            station_1_index=p-1,
                                            station_2_index=q-1,
                                            # corr_index=self._MS_corr_index,
                                            output_col=output_col)
        self._matrixet = self._ns[name]

        
        # The single VisDataMux node is the actual interface node.
        self._ns[vdm] << Meq.VisDataMux(*[self._matrixet(*ifr) for ifr in self.ifrs()]);

        # Return the actual name of the VisDataMux (needed for tree execution)
        return vdm


    #--------------------------------------------------------------------------

    def insert_accumulist_reqseq (self, key=None, qual=None):
        """Insert a series of reqseq node(s) with the children accumulated
        in self._accumulist (see Matrixet22). The reqseqs will get the current
        matrix nodes as their last child, to which their result is transmitted."""

        cc = self.accumulist(key=key, clear=False)
        n = len(cc)
        if n>0:
            quals = self.quals(append=qual)
            cc.append('placeholder')
            name = 'reqseq'
            if isinstance(key, str): name += '_'+str(key)
            for ifr in self.ifrs():
                cc[n] = self._matrixet(*ifr)         # fill in the placeholder
                self._ns[name](*quals)(*ifr) << Meq.ReqSeq(children=cc, result_index=n,
                                                           cache_num_active_parents=1)
            self._matrixet = self._ns[name](*quals)
        return True

    #--------------------------------------------------------------------------

    def fill_with_identical_matrices (self, name='initial', coh=None):
        """Fill with 2x2 complex unit matrices"""
        quals = self.quals()
        if coh==None:
            coh = self._ns.unit_matrix(*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                               complex(0.0),complex(1.0))
        self._matrixet = self._ns[name](*quals) 
        for ifr in self.ifrs():
            self._matrixet(*ifr) << Meq.Identity(coh)
        return True

    #---------------------------------------------------------------------------

    def addGaussianNoise (self, stddev=0.1, qual=None, visu=True):
        """Add gaussian noise with given stddev to the internal cohset"""
        if stddev>0.0:
            quals = self.quals(append=qual)
            name = 'addGaussianNoise22'
            kwqual = dict(stddev=stddev)
            matrels = self.matrel_keys()
            for ifr in self.ifrs():
                mm = range(4)
                for i in range(4):
                    m = matrels[i]
                    rnoise = self._ns.rnoise(*quals)(**kwqual)(*ifr)(m) << Meq.GaussNoise(stddev=stddev)
                    inoise = self._ns.inoise(*quals)(**kwqual)(*ifr)(m) << Meq.GaussNoise(stddev=stddev)
                    mm[i] = self._ns.noise(*quals)(**kwqual)(*ifr)(m) << Meq.ToComplex(rnoise,inoise)
                noise = self._ns.noise(*quals)(**kwqual)(*ifr) << Meq.Matrix22(*mm)
                self._ns[name](*quals)(**kwqual)(*ifr) << Meq.Add(self._matrixet(*ifr),noise)
            self._matrixet = self._ns[name](*quals)(**kwqual)           
            if visu: return self.visualize(name)
        return None

    #...........................................................................

    def corrupt (self, joneset=None, qual=None, visu=False):
        """Corrupt the internal matrices with the matrices of the given Joneset22 object.
        Transfer the parmgroups of the Joneset22 to its own ParmGroupManager (pgm)."""
        quals = self.quals(append=qual)
        qq = joneset.quals()
        for q in qq:
            if not q in quals: quals.append(q)
        name = 'corrupt22'
        jmat = joneset.matrixet() 
        for ifr in self.ifrs():
            j1 = jmat(ifr[0])
            j2c = jmat(ifr[1])('conj') ** Meq.ConjTranspose(jmat(ifr[1])) 
            self._ns[name](*quals)(*ifr) << Meq.MatrixMultiply(j1,self._matrixet(*ifr),j2c)
        self._matrixet = self._ns[name](*quals)              
        # Transfer any parmgroups (used by the solver downstream)
        self._pgm.merge(joneset._pgm)
        if visu: return self.visualize(name)
        return None

    #...........................................................................

    def correct (self, joneset=None, qual=None, visu=False):
        """Correct the internal matrices with the matrices of the given Joneset22 object."""
        quals = self.quals(append=qual)
        qq = joneset.quals()
        for q in qq:
            if not q in quals: quals.append(q)
        name = 'correct22'
        jmat = joneset.matrixet()
        for ifr in self.ifrs():
            j1i = jmat(ifr[0])('inv') ** Meq.MatrixInvert22(jmat(ifr[0]))
            j2c = jmat(ifr[1])('conj') ** Meq.ConjTranspose(jmat(ifr[1])) 
            j2ci = j2c('inv') ** Meq.MatrixInvert22(j2c)
            self._ns[name](*quals)(*ifr) << Meq.MatrixMultiply(j1i,self._matrixet(*ifr),j2ci)
        self._matrixet = self._ns[name](*quals)              
        # Transfer any accumulist entries (e.g. visualisation dcolls etc)
        # self.merge_accumulist(joneset)
        if visu: return self.visualize(name)
        return None






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
        vis.corrupt(jones, visu=True)
        vis.addGaussianNoise(stddev=0.05, visu=True)
        vis.display('after corruption')
        if False:
            vis.correct(jones, visu=True)

    if True:
        pred = Visset22(ns, label='nominal', quals='xxc', array=array, cohset=cohset)
        pred.display('initial')
        G = Joneset22.GJones(ns, stations=array.stations(), simulate=False)
        D = Joneset22.DJones(ns, stations=array.stations(), simulate=False)
        jones = G
        jones = D
        jones = Joneset22.Joneseq22([G,D])
        pred.corrupt(jones, visu=True)
        vis.display('after corruption')
        if True:
            vis.correct(jones, visu=True)

    if True:
        vis.insert_accumulist_reqseq()
  
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
        if not cohset:
            vis.fill_with_identical_matrices()
        vis.display()

    if 1:
        G = Joneset22.GJones (ns, stations=array.stations(), simulate=True)
        vis.corrupt(G, visu=True)
        # vis.addGaussianNoise(stddev=0.05, visu=True)
        vis.correct(G, visu=True)
        vis.display('after corruption')

    if 1:
        vis.insert_accumulist_reqseq()
        vis.display(full=True)
        

    if 0:
        G = Joneset22.GJones (ns, stations=array.stations(), simulate=True)
        D = Joneset22.DJones (ns, stations=array.stations(), simulate=True)
        jones = Joneset22.Joneseq22([G,D])
        vis.corrupt(jones, visu=True)
        vis.display('after corruption')


#=======================================================================
# Remarks:

#=======================================================================
