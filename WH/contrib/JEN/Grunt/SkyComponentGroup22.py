# file: ../Grunt/SkyComponentGroup22.py

# History:
# - 04feb2007: creation (from PointSource22.py) 

# Description:

# The SkyComponentGroup22 class represents a group of Meow SkyComponents.
# It is a virtual base class for a series of more specialized classes that
# represent various groups of SkyComponents (e.g. a grid for testing).
# It has various options for modifying its source pattern, e.g. rotation
# translation, magnification, etc.
# It is not a Meow Patch, but it can generate one. In addition, it can makes
# a Visset22 with a ParmGroupManager, so we can solve for its source parameters
# in the Grunt system.
# It also has support for making subsets of its sources, for peeling. These
# can also be turned into Meow Patches and/or Grunt Visset22 objects.
 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import ParmGroupManager

import math
import random


# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

def include_TDL_options(prompt='definition'):
    """Instantiates user options for the meqbrouwser"""
    predefined = ['unpol','Q','U','V','QU','QUV','UV','QV']
    predefined.extend(['3c147','3c286'])
    predefined.append(None)
    menuname = 'SkyComponentGroup22 ('+prompt+')'
    TDLCompileMenu(menuname,
                   TDLOption('TDL_predefined',"predefined source",predefined),
                   TDLOption('TDL_StokesI',"Stokes I (Jy)",[1.0,2.0,10.0], more=float),
                   TDLOption('TDL_StokesQ',"Stokes Q (Jy)",[None, 0.0, 0.1], more=float),
                   TDLOption('TDL_StokesU',"Stokes U (Jy)",[None, 0.0, -0.1], more=float),
                   TDLOption('TDL_StokesV',"Stokes V (Jy)",[None, 0.0, 0.02], more=float),
                   TDLOption('TDL_spi',"Spectral Index (I=I0*(f/f0)**(-spi)",[0.0, 1.0], more=float),
                   TDLOption('TDL_freq0',"Reference freq (MHz) for Spectral Index",[None, 1.0], more=float),
                   TDLOption('TDL_RM',"Intrinsic Rotation Measure (rad/m2)",[None, 0.0, 1.0], more=float),
                   TDLOption('TDL_source_name',"source name (overridden by predefined)", ['PS22'], more=str),
                   );
    return True


#======================================================================================

class SkyComponentGroup22 (object):
    """Virtual base class for specialised groups of SkyComponents"""

    def __init__(self, ns, name='SkyComponentGroup22', observation=None):

        self._ns = ns
        self._name = name
        # self._observation = observation             # .....??

        self._skycomp = []
        self._ll = []
        self._mm = []
        self._wgt = []
        # self._unit = 'arcmin'

        # Some placeholders:
        self._Patch = None
        self._Visset22 = None

        # Create a Grunt ParmGroupManager object:
        self._pgm = None
        # self._pgm = ParmGroupManager.ParmGroupManager(ns, label=name)

        # Finished:
        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self._name)
        ss += ' (n='+str(self.len())+')'
        return ss


    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print '** SkyComponents ('+str(self.len())+'):'
        for k,sc in enumerate(self._skycomp):
            print '  - '+str(k)+': '+str(sc)
        for k in range(self.len()):
            print '  - '+str(k)+': l='+str(self._ll[k])+' m='+str(self._mm[k])+' wgt='+str(self._wgt[k])
        print '**\n'
        return True

    #--------------------------------------------------------------------------

    def len(self):
        """Return the nr of sources in the group"""
        return len(self._skycomp)

    #--------------------------------------------------------------------------
    
    def add_PointSource (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Meow PointSource object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        sc_dir = Meow.LMDirection(self._ns, name, l, m)
        skycomp = Meow.PointSource(self._ns, name, sc_dir)
        return self.add(skycomp, l=l, m=m, wgt=wgt)

    def add (self, skycomp, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a SkyComponent object to the group"""
        self._skycomp.append(skycomp)
        self._ll.append(l)
        self._mm.append(m)
        self._wgt.append(wgt)
        return self.len()



    #--------------------------------------------------------------------------
    # Some operations on the source coordinates:
    #--------------------------------------------------------------------------

    def rotate(self, angle=0.0):
        """Rotate the group (l,m) around (0,0) by an angle (rad)"""
        sina = math.sin(angle)
        cosa = math.cos(angle)
        for k in range(self.len()):
            l = self._ll[k]*cosa - self._mm[k]*sina
            self._mm[k] = self._ll[k]*sina + self._mm[k]*cosa
            self._ll[k] = l
        return True

    def translate(self, dl=0.0, dm=0.0):
        """Translate the group (l,m) by the specified (dl,dm)"""
        for k in range(self.len()):
            self._ll[k] += dl
            self._mm[k] += dm
        return True

    def magnify(self, ml=1.0, mm=1.0):
        """Magnify the group (l,m) w.r.t (0,0) by the specified factors (ml,mm)"""
        for k in range(self.len()):
            self._ll[k] *= ml
            self._mm[k] *= mm
        return True


    #--------------------------------------------------------------------------

    def Meow_Patch (self, observation=None):
        """Generate a Meow Patch from the sources in this group"""
        if not self._Patch:
            self._Patch = Meow.Patch(ns, self._name, self._observation.phase_centre)
            for src in self._src:
                self._Patch.add(src)
        return self._Patch


    #--------------------------------------------------------------------------

    def Visset22 (self, array, observation, name=None, visu=False):
        """Create a Visset22 object from the visibilities generated by this SkyComponentGroup22"""
        if not self._Visset22:                   # avoid duplication
            polrep = 'linear'
            if observation.circular():
                polrep = 'circular'
            # Make the Visset22:
            # NB: Use the ORIGINAL nodescope (self.ns0), not the Qualscope (self.ns)
            #     See Meow.Parametrization.py
            if not name: name = self._pp['name']
            self._Visset22 = Visset22.Visset22 (self.ns0, quals=[], label=name,
                                                polrep=polrep, simulate=self._simulate,
                                                array=array, observation=observation)
            # Make the 2x2 visibility matrices per ifr:
            if False:
                # Use this if the source has to be shifted (KJones):
                matrixet = self.visibilities(array,observation)
                self._Visset22.matrixet(new=matrixet)
            else:
                # Use this if the source is in the phase centre (no KJones):
                matrix = self.coherency(observation)
                self._Visset22.fill_with_identical_matrices ('PS22_visibility', matrix)

            # ParmGroupManager... (get all MeqParms from self.ns...?)
            # NB: Not if self._simulate==True (i.e. hide the MeqParms)

            if visu: self._Visset22.visualize('SkyComponentGroup22')
        return self._Visset22


    #---------------------------------------------------------------------------------
    
    def test (self):
        """Helper routine to add some test sources to the group"""
        scg.add_PointSource('first', 1,1)
        scg.add_PointSource('second', 1,0)
        scg.add_PointSource('third', 0,1)
        return True










#======================================================================================
#======================================================================================

class PointSourceGroup22 (SkyComponentGroup22):
    """A SkyComponentGroup22 with a pattern of point-sources of the same type, for testing.
    This is a virtual base-class for a range of more specific source patterns."""

    def __init__(self, ns, name='SkyComponentGroup22', direction=None,
                 simulate=False, **pp):

        # Initialise its Meow counterpart:
        SkyComponentGroup22.__init__(self, ns=ns, name=name)

        # Finished:
        return None


    def include_TDL_options (self):
        """Re-implementation of the base class function. Include the TDL options
        for a PointSource22 object."""
        return True








#===============================================================
# Test routine (with meqbrowser):
#===============================================================

# include_TDL_options('test')

def _define_forest(ns):

    cc = []

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    observation = Meow.Observation(ns)
    direction = Meow.LMDirection(ns, TDL_source_name, l=1.0, m=1.0)
    ps = SkyComponentGroup22 (ns, name='test',
                  direction=direction)
    ps.display()

    vis = ps.Visset22(array, observation)
    vis.display()
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
        num_stations = 3
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        Meow.Context.set (array, observation)
        src = 'unpol' 
        src = 'QUV'
        # direction = Meow.LMDirection(ns, src, l=1.0, m=1.0)
        scg = SkyComponentGroup22 (ns, name='test')
        scg.test()
        scg.translate(1,1)
        scg.display()
        scg.rotate(1)
        scg.display()

    if 0:
        vis = scg.Visset22(array, observation)
        vis.display()


#=======================================================================
# Remarks:

#=======================================================================
