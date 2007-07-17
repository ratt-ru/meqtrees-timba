# file: ../Grunt/Visset22.py

# History:
# - 05jan2007: creation (from JEN_SolverChain.py)
# - 14mar2007: added MSSE support (sigma) to .corrupt()
# - 26mar2007: adapted for QualScope
# - 07jun2007: adapted to NodeList/ParameterizationPlus
# - 17jul2007: adapted to ._pgm.

# Description:

# The Visset22 class encapsulates a set of 2x2 cohaerency matrices,
# i.e. visbilities. It is derived from the Matrixet22 class.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Matrixet22
from Timba.Contrib.JEN.Grunt import display

from copy import deepcopy

# For testing only:
import Meow
from Timba.Contrib.JEN.Grunt import Joneset22



#======================================================================================

class Visset22 (Matrixet22.Matrixet22):
    """Class that represents a set of 2x2 Cohaerency  matrices"""

    def __init__(self, ns, name='<v>', quals=[], kwquals={}, 
                 cohset=None, array=None,
                 # observation=None,
                 polrep=None):

        # self._array = array                             # Meow IfrArray object
        self._array = Meow.Context.get_array(array)
        ## self._observation = observation              # Meow Observation object

        # Some specific Visset22 attributes:
        self._MS_corr_index = [0,1,2,3]                 # see make_spigots/make_sinks
        self._stations = array.stations()               # convenience only ...?           

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, name,
                                       quals=quals, kwquals=kwquals,
                                       polrep=polrep, indices=array.ifrs())

        self._corrs = self._matrix_elements['name']     # e.g. ['XX','XY','YX','YY']

        if cohset:
            # If supplied, fill in the Matriset22 matrices, otherwise leave at None
            self._matrixet = cohset

        # The direction of the uv-data phase-centre (Meow.(LM(Approx))Direction object):
        # This is changed whenever the phase centre is shifted (see below).
        self._dir0 = Meow.Context.get_dir0(None)
        if not self._dir0:
            self._dir0 = Meow.LMApproxDirection(ns, self.name+'_dir0', l=0.0, m=0.0)
        self._dir00 = self._dir0                        # see .restore_phase_centre()
        if not isinstance(self._dir00, Meow.LMApproxDirection):
            self._dir00 = Meow.LMApproxDirection(ns, self.name+'_dir00', l=0.0, m=0.0)
        self._last_dir0 = None                          # see .restore_phase_centre()

        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.name)
        ss += '  pols='+str(self._pols)
        ss += '  nstat='+str(len(self.stations()))
        ss += '  nifr='+str(len(self.ifrs()))
        ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations: '+str(self.stations())
        print '   - _corrs: '+str(self._corrs)
        print '   - MS_corr_index: '+str(self._MS_corr_index)
        print '   - Current phase centre (dir0): '+str(self._dir0)
        if full:
            display.subtree(self._dir0.lmn(), txt='dir0.lmn',
                            skip_line_after=False, show_initrec=True)
            print '   - Last phase centre: '+str(self._last_dir0)
            if self._last_dir0:
                display.subtree(self._last_dir0.lmn(), txt='last_dir0.lmn',
                                skip_line_after=False, show_initrec=True)
        

        return True 

    #--------------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        return self._stations                             

    def ifrs (self, select='all'):
        """Get (a selection of) ifrs (station-pairs)"""
        ifrs = self.indices()              
        # ..... do the selection .....
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
        self.history('.make_spigots('+str(input_col)+')')

        self._MS_corr_index = MS_corr_index    # Keep. See also .make_sinks()

        qnode = self._nextstage(name='spigots')['qnode']
        for p,q in self.ifrs():
            qnode(p,q) << Meq.Spigot(station_1_index=p-1,
                                     station_2_index=q-1,
                                     # corr_index=self._MS_corr_index,
                                     # flag_bit=flag_bit,
                                     input_column=input_col)
        self._matrixet = qnode

        if False:
            # Optional: insert a dummy node after the spigot for testing
            qnode = self._nextstage(name='dummy')['qnode']
            for p,q in self.ifrs():
                qnode(p,q) << Meq.Identity(self._matrixet(p,q))
            self._matrixet = qnode


        # self.create_ReadVisHeader_placeholders()    # see below....

        if visu:
            self.visualize(visu, quals=self.stagename())
        return True

    #--------------------------------------------------------------------------

    def create_ReadVisHeader_placeholders(self):
        """Create placeholder nodes expected by ReadVisHeader.py"""
        # nodes for phase centre
        self.ns.radec0 = Meq.Composer(self.ns.ra<<0, self.ns.dec<<0)
        
        # nodes for array reference position
        self.ns.xyz0 = Meq.Composer(self.ns.x0<<0,
                                     self.ns.y0<<0,
                                     self.ns.z0<<0)
        
        # now define per-station stuff: XYZs and UVWs 
        for p in ANTENNAS:
            self.ns.xyz(p) << Meq.Composer(self.ns.x(p)<<0,
                                            self.ns.y(p)<<0,
                                            self.ns.z(p)<<0)
            self.ns.uvw(p) << Meq.UVW(radec=self.ns.radec0,
                                       xyz_0=self.ns.xyz0,
                                       xyz=self.ns.xyz(p))

        return True

    #--------------------------------------------------------------------------

    def make_sinks (self, output_col='DATA', 
                    # start=None, pre=None, post=None,
                    vdm='vdm', visu=False):
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
        self.history('.make_sinks('+str(output_col)+')')

        # First attach any nodes collected in the 'accumulist' to a ReqSeq,
        # which is then inserted in the matrixet main stream (i.e. all ifrs).
        # The collected nodes are usually solver nodes or dataCollect nodes.
        # The ReqSeq will execute them in that order before executing the current
        # main-stream matrix node. The result of the latter is the only one
        # that is transmitted by the ReqSeq. The accumulist is cleared.
        self.insert_accumulist_reqseq(visu=visu, name='sinks')

        # Make the sinks:
        qnode = self._nextstage(name='sink')['qnode']
        for p,q in self.ifrs():
            qnode(p,q) << Meq.Sink(self._matrixet(p,q),
                                   station_1_index=p-1,
                                   station_2_index=q-1,
                                   # corr_index=self._MS_corr_index,
                                   output_col=output_col)
        self._matrixet = qnode

        
        # The single VisDataMux node is the actual interface node.
        vdm = self.ns0[vdm] << Meq.VisDataMux(*[self._matrixet(*ifr) for ifr in self.ifrs()]);

        # Return the actual name of the VisDataMux (needed for tree execution)
        return vdm.name


    #--------------------------------------------------------------------------

    def fill_with_identical_matrices (self, name='initial', stddev=0.0,
                                      coh=None, visu=False):
        """Fill the Visset22 with 2x2 identical matrices. If coh==None, these are
        complex unit matrices. Otherwise, assume that coh is a 2x2 matrix, and use that.
        If stddev>0, add gaussian noise with this stddev."""

        self.history('.fill_with_identical_matrices('+str(coh)+')')
        if coh==None:
            coh = self.ns.unit_matrix << Meq.Matrix22(complex(1.0),complex(0.0),
                                                       complex(0.0),complex(1.0))
                
        qnode = self._nextstage(name=name)['qnode']
        self._matrixet = qnode
        for ifr in self.ifrs():
            self._matrixet(*ifr) << Meq.Identity(coh)
        if stddev>0:
            self.addGaussianNoise (stddev=stddev, quals=None, visu=False)
        if visu: return self.visualize(visu, quals=self.stagename())
        return True

    #---------------------------------------------------------------------------

    def addGaussianNoise (self, stddev=0.1, quals=None, visu=True):
        """Add gaussian noise with given stddev to the internal cohset"""
        if stddev>0.0:
            self.history('.addGaussianNoise('+str(stddev)+')')
            name = 'addGaussianNoise'
            qnode = self._nextstage(name=name, quals=quals,
                                    kwquals=dict(stddev=stddev))['qnode']
            for ifr in self.ifrs():
                noise = qnode('noise')(*ifr)
                mm = range(4)
                for i in range(4):
                    m = self._corrs[i]
                    rnoise = noise(m)('real') << Meq.GaussNoise(stddev=stddev)
                    inoise = noise(m)('imag') << Meq.GaussNoise(stddev=stddev)
                    mm[i] = noise(m) << Meq.ToComplex(rnoise,inoise)
                noise << Meq.Matrix22(*mm)
                qnode(*ifr) << Meq.Add(self._matrixet(*ifr),noise)
            self._matrixet = qnode           
            if visu: return self.visualize(visu, quals=self.stagename())
        return None

    #...........................................................................

    def restore_phase_centre (self, quals='restore', last=True, visu=False):
        """Restore the uv-data phase-centre to an earlier position (Direction).
        - if last==True, shift back to the direction before the last shift_phase_centre().
        - otherwise, shift back to the original (observation) phase-centre.
        If the phase-centre has not yet been shifted, do nothing."""
        self.history('.restore_phase_centre(last='+str(last)+')')
        if not self._last_dir0:
            return False           # The phase centre has not been shifted yet: do nothing.
        elif last:
            dir0 = self._last_dir0 # Back to the direction before the last .shift_phase_centre()
        else:
            dir0 = self._dir00     # Back to the original (observation) phase centre
        return self.shift_phase_centre (lmdir=dir0, quals=quals, visu=visu)


    def shift_phase_centre (self, lmdir, quals=None, visu=False):
        """Shift the phase-centre of the uv-data from its current position
        (defined by the internal Direction object self._dir0) to the position
        defined by the given LMDirection object (lmdir).
        Replace self._dir0 with lmdir, so that cumulative shifts are possible."""

        self.history('.shift_phase_centre()')
        qnode = self._nextstage(name='shifted', quals=quals)['qnode']
        lmdir.make_phase_shift(qnode, vis0=self._matrixet,
                               array=self._array, dir0=self._dir0) 
        self._matrixet = qnode
        self._last_dir0 = self._dir0       # Keep for use by restore_phase_centre()
        self._dir0 = lmdir                 # The new uv-data phase centre
        self.display('vis.shift_phase_centre() to: '+lmdir.name, full=True)
        if visu: return self.visualize(visu, quals=self.stagename())
        return None


    #...........................................................................


    def subtract_mean (self, quals=None, lmdir=None, restore=False, visu=False):
        """Subtract the mean over (the domain) from the uv-data.
        This is a dirty way to get rid of flux at the current phase
        centre (like UVLIN in AIPS). If a phase centre (lmdir) is
        specified (as an LMDirection) the phase-centre of the uv-data
        will be shifted there and back."""
        lmname = None
        if lmdir:
            self.shift_phase_centre (lmdir, quals=quals, visu=False)
            lmname = lmdir.name
        self.history('.subtract_mean()')
        name = 'subtract_mean'
        qnode = self._nextstage(name=name, quals=quals)['qnode']
        for ifr in self.ifrs():
            mean = qnode(*ifr)('mean') << Meq.Mean(self._matrixet(*ifr))
            qnode(*ifr) << Meq.Subtract(self._matrixet(*ifr),mean)
        self._matrixet = qnode              
        if visu: return self.visualize(visu, quals=self.stagename())
        if lmdir and restore:
            self.restore_phase_centre (last=True, quals=quals, visu=False)
        return None


    #...........................................................................

    def corrupt (self, joneset=None, quals=None, visu=False):
        """Corrupt the internal matrices with the matrices of the given Joneset22 object.
        Merge the parmgroups of the Joneset22 with its own set."""
        self.history('.corrupt()')
        self.history(subappend=joneset.history())
        name = 'corrupt22'
        qnode = self._nextstage(name=name, quals=quals, other=joneset)['qnode']
        jmat = joneset.matrixet() 
        for ifr in self.ifrs():
            j1 = jmat(ifr[0])
            j2c = jmat(ifr[1])('conj') ** Meq.ConjTranspose(jmat(ifr[1])) 
            qnode(*ifr) << Meq.MatrixMultiply(j1,self._matrixet(*ifr),j2c)
        self._matrixet = qnode              
        # Transfer any accumulist entries (e.g. visualisation dcolls etc)
        self._pgm.merge_accumulist(joneset)
        # Transfer any parmgroups (used by the solver downstream)
        self._pgm.merge(joneset)                                    
        if visu: return self.visualize(visu, quals=self.stagename())
        return None

    #...........................................................................

    def correct (self, joneset=None, quals=None,
                 sigma=None, pgm_merge=False, visu=False):
        """Correct the internal matrices with the matrices of the given Joneset22 object.
        If sigma is specified (number or node), add a unit matrix multiplied by the
        estimated noise (sigma**2) before inversion (MMSE)."""

        self.history('.correct('+str(sigma)+' '+str(pgm_merge)+')')
        self.history(subappend=joneset.history())

        # Robust correction (MSSE):
        if sigma:
            sigma2 = ns.sigma2_MSSE << (sigma*sigma)
            MSSE = ns.MSSE << Meq.Matrix22(sigma2,0.0,0.0,sigma2)
            
        name = 'correct22'
        qnode = self._nextstage(name=name, quals=quals, other=joneset)['qnode']
        jmat = joneset.matrixet()
        for ifr in self.ifrs():
            if sigma:
                j1i = jmat(ifr[0])('MSSE') ** Meq.MatrixMultiply(jmat(ifr[0]),MSSE)
                j1i = jmat(ifr[0])('inv_MSSE') ** Meq.MatrixInvert22(j1i)
            else:
                j1i = jmat(ifr[0])('inv') ** Meq.MatrixInvert22(jmat(ifr[0]))
            j2c = jmat(ifr[1])('conj') ** Meq.ConjTranspose(jmat(ifr[1])) 
            j2ci = j2c('inv') ** Meq.MatrixInvert22(j2c)
            qnode(*ifr) << Meq.MatrixMultiply(j1i,self._matrixet(*ifr),j2ci)
        self._matrixet = qnode              

        if pgm_merge:
            # Transfer any parmgroups (used by the solver downstream)
            # NB: Only True for redundancy-solution (see WSRT_redun.py)
            self._pgm.merge(joneset)
        # Transfer any accumulist entries (e.g. visualisation dcolls etc)
        self._pgm.merge_accumulist(joneset)
        if visu: return self.visualize(visu, quals=self.stagename())
        return None


    #--------------------------------------------------------------------------

    def insert_accumulist_reqseq (self, key=None, quals=None, visu=False, name='accumulist'):
        """Insert a series of reqseq node(s) with the children accumulated
        in self._accumulist (see ParameterizationPlus). The reqseqs will get the current
        matrix nodes as their last child, to which their result is transmitted."""

        self.history('.insert_accumulist_reqseq('+str(key)+' '+str(name)+')')

        # If visu==True, append the visualisation dcoll to the accumulist,
        # so that it will get the last request before the main-stream is addressed.
        if visu: self.visualize(visu, quals=self.stagename())
        
        cc = self._pgm.accumulist(key=key, clear=False)
        n = len(cc)
        if n>0:
            cc.append('placeholder')
            name = 'reqseq'
            qnode = self._nextstage(name=name, quals=quals)['qnode']
            if isinstance(key, str): name += '_'+str(key)
            for ifr in self.ifrs():
                cc[n] = self._matrixet(*ifr)         # fill in the placeholder
                qnode(*ifr) << Meq.ReqSeq(children=cc, result_index=n,
                                          cache_num_active_parents=1)
            self._matrixet = qnode
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
    Meow.Context.set(array, observation)

    cohset = None
    if 0:
        allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
        l = 1.0
        m = 1.0
        src = '3c84'
        src_dir = Meow.LMDirection(ns, src, l, m)
        source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
        allsky.add(source)
        cohset = allsky.visibilities(array, observation)

    vis = Visset22(ns, 'test',
                   # quals='yyc',
                   array=array, cohset=cohset)
    if not cohset:
        vis.fill_with_identical_matrices()

    if 0:
        vis.addGaussianNoise()
    vis.display('initial')

    if 0:
        vis.subtract_mean(visu=True)
        vis.display(recurse=5)

    if 1:
        G = Joneset22.GJones(ns, stations=array.stations(), mode='simulate')
        # D = Joneset22.DJones(ns, stations=array.stations(), mode='simulate')
        jones = G
        # jones = D
        # jones = Joneset22.Joneseq22([G,D])
        vis.corrupt(jones, visu=True)
        # vis.addGaussianNoise(stddev=0.05, visu=True)
        vis.display('after corruption')
        if 1:
            vis.correct(jones, visu=True)
            vis.display('after correction')

    if 0:
        pred = Visset22(ns, 'nominal', quals='xxc', array=array, cohset=cohset)
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
        Meow.Context.set(array, observation)
        cohset = None
        if 0:
            allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
            l = 1.0
            m = 1.0
            src = '3c84'
            src_dir = Meow.LMDirection(ns, src, l, m)
            source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
            allsky.add(source)
            cohset = allsky.visibilities(array, observation)
        vis = Visset22(ns, 'test',
                       # quals='yut',
                       polrep='circular',
                       array=array, cohset=cohset)
        if not cohset:
            vis.fill_with_identical_matrices()
        vis.display()

    if 0:
        vis.addGaussianNoise()
        vis.display(recurse=5)

    if 0:
        lmdir = Meow.LMDirection(ns, 'shift_test', l=0.01, m=-0.02)
        print '** lmdir =',str(lmdir)
        vis.shift_phase_centre (lmdir, quals=None, visu=False)
        vis.display('after shift', full=True)

    if 1:
        G = Joneset22.GJones (ns, stations=array.stations(),
                              # telescope='WSRT', band='90cm',
                              mode='simulate')
                              # mode='simulate')
        if 1:
            vis.corrupt(G, visu=True)
            # vis.addGaussianNoise(stddev=0.05, visu=True)
            vis.correct(G, visu=True)
        if 0:
            sigma = 0.1
            # sigma = ns.SIGMA << 0.1
            vis.correct(G, quals='ccc', sigma=sigma, visu=True)
        vis.display('after correction', recurse=5)
        vis.history().display(full=True)

    if 0:
        vis.insert_accumulist_reqseq()
        vis.display(full=True)
        

    if 0:
        G = Joneset22.GJones (ns, stations=array.stations(), mode='simulate')
        D = Joneset22.DJones (ns, stations=array.stations(), mode='simulate')
        jones = Joneset22.Joneseq22([G,D])
        vis.corrupt(jones, visu=True)
        vis.display('after corruption')

    if 1:
        vis.history().display(full=True)


#=======================================================================
# Remarks:

#=======================================================================
