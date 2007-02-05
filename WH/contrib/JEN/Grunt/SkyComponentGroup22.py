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
from Timba.Contrib.JEN.Grunt import PointSource22

import math
import random
from copy import deepcopy


# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

class SkyComponentGroup22 (object):
    """Virtual base class for specialised groups of SkyComponents"""

    def __init__(self, ns, name='SkyComponentGroup22', **pp):

        self._ns = ns
        self._name = name
        self._observation = Meow.Context.get_observation(None)    # ....??

        # Deal with input arguments (default set by TDL_options):
        # (But they may also be set via **pp)
        self._pp = deepcopy(pp)
        if not isinstance(self._pp, dict): self._pp = dict()
        # self._pp.setdefault('peeling_group', TDL_peeling_group)

        # Initialise the skycomp list(s):
        self._skycomp = []
        self._sc_name = []
        self._ll = []
        self._mm = []
        self._wgt = []
        # self._unit = 'arcmin'

        # Some placeholders:
        self._Patch = None
        self._Visset22 = None
        self._peeling_group = []
        self._peeling_Patch = []
        self._peeling_Visset22 = []

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
        print '** Input arguments ('+str(len(self._pp))+'):'
        for key in self._pp.keys():
            print '  - pp['+key+'] = '+str(self._pp[key])
        print '** SkyComponents ('+str(self.len())+'):'
        for k,sc in enumerate(self._skycomp):
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+str(sc)
        for k in range(self.len()):
            s1 = ' wgt='+str(self._wgt[k])
            s1 += '   l='+str(self._ll[k])+'   m='+str(self._mm[k])
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+s1
        print '** Peeling support ('+str(len(self._peeling_Patch))+'):'
        for k,pp in enumerate(self._peeling_Patch):
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+str(self._peeling_group[k])
        for k,pp in enumerate(self._peeling_Patch):
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+str(pp)
        for k,pv in enumerate(self._peeling_Visset22):
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+str(pv.oneliner())
        print '** Optimum image size: '+str(self.imagesize())+' arcmin'
        print '**\n'
        return True

    #--------------------------------------------------------------------------

    def len(self):
        """Return the nr of sources in the group"""
        return len(self._skycomp)

    def skycomp(self, index=0):
        """Return the specified (index) SkyComponent from the list"""
        return self._skycomp[index]

    def add (self, skycomp, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a SkyComponent object to the group"""
        self._skycomp.append(skycomp)
        self._sc_name.append(name)
        self._ll.append(l)
        self._mm.append(m)
        self._wgt.append(wgt)
        return self.len()

    #--------------------------------------------------------------------------
    # Some virtual methods (to be re-implemented)
    #--------------------------------------------------------------------------

    def imagesize (self):
        """Returns the optimum image size, based on grid size and step.
        This is a virtual method, to be re-implemented by the specialized
        classes that are derived from this class."""
        # return grid_size*grid_step            # see WorkShop2007 ME2 sky_models.py
        return 10.0                             # safe number (arcmin!)


    def include_TDL_options (self, prompt='definition'):
        """Instantiates user options for the meqbrouwser.
        This is a virtual method, to be re-implemented by the specialized
        classes that are derived from this class."""
        return True


    #--------------------------------------------------------------------------
    # Functions for adding SkyComponents to the list:
    #--------------------------------------------------------------------------

    def add_PointSource (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Meow PointSource object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        direction = Meow.LMDirection(self._ns, name, l, m)
        # NB: Parameters are made for I with tag 'flux'
        # NB: Parameters are made for Q,U,V with tag 'flux pol'
        # NB: Parameters are made for si with tag 'spectrum'
        # NB: Parameters are made for RM with tag 'pol'
        skycomp = Meow.PointSource(self._ns, name, direction,
                                   I=0.0, Q=None, U=None, V=None,
                                   spi=None, freq0=None, RM=None)
        return self.add(skycomp, name=name, l=l, m=m, wgt=wgt)


    def add_GaussianSource (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Meow GaussianSource object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        direction = Meow.LMDirection(self._ns, name, l, m)
       # NB: Parameters are made with tag 'shape'
        skycomp = Meow.GaussianSource(self._ns, name, direction,
                                      size=(1.0,2.0),              # <------
                                      phi=0, symmetric=False,
                                      I=0.0, Q=None, U=None, V=None,
                                      spi=None, freq0=None, RM=None)
        return self.add(skycomp, name=name, l=l, m=m, wgt=wgt)


    def add_PointSource22 (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Grunt PointSource22 object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        direction = Meow.LMDirection(self._ns, name, l, m)
        skycomp = PointSource22.PointSource22(self._ns, name=name,
                                              direction=direction)
        return self.add(skycomp, name=name, l=l, m=m, wgt=wgt)




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
    # Make visibilities (via the Meow Patch)
    #--------------------------------------------------------------------------

    def visibilities (self, array, observation=None):
        """Return 'Meow' visibilities, i.e. as an unqualified node"""
        self.Meow_Patch(observation)
        return self._Patch.visibilities(array, observation)


    def Visset22 (self, array=None, observation=None, name=None, visu=True):
        """Create a Visset22 object from the visibilities generated by this SkyComponentGroup22"""
        if not self._Visset22:                   # avoid duplication
            self.Meow_Patch(observation)         # make sure of self._Patch
            self._Visset22 = self.Patch2Visset22 (self._Patch, array=array,
                                                  observation=observation,
                                                  name=name, visu=visu)
        return self._Visset22


    def Patch2Visset22 (self, Patch, array, observation=None, name=None, visu=True):
        """Helper function to create a Grunt Visset22 object from the given Meow Patch"""
        polrep = 'linear'
        if observation.circular():
            polrep = 'circular'

        # Make the Visset22:
        if not name: name = self._name
        vis = Visset22.Visset22 (self._ns, quals=[], label=name,
                                 polrep=polrep,
                                 # simulate=self._simulate,
                                 array=array, observation=observation)
        # Make the 2x2 visibility matrices per ifr:
        matrixet = Patch.visibilities(array,observation)
        vis.matrixet(new=matrixet)

        # ParmGroupManager... (get all MeqParms from self.ns...?)
        # NB: Not if self._simulate==True (i.e. hide the MeqParms)

        if visu: vis.visualize('SkyComponentGroup22')
        return vis


    def Meow_Patch (self, observation=None):
        """Generate a single Meow Patch from the sources in this group"""
        if not self._Patch:
            if observation:
                self._Patch = Meow.Patch(self._ns, self._name,
                                         observation.phase_centre)
            else:
                self._Patch = Meow.Patch(self._ns, self._name,
                                         self._observation.phase_centre)
            for skycomp in self._skycomp:
                self._Patch.add(skycomp)
        return self._Patch


    #--------------------------------------------------------------------------
    # Peeling support:
    #--------------------------------------------------------------------------

    def make_peeling_Patches (self, window=1):
        """For each skycomp in the list, a peeling patch may be defined.
        A peeling patch contains at least the source itself (window=1).
        In addition, it may also contain a small number (<=window-1) of fainter
        sources. The idea is to reduce contamination by those fainter sources
        when solving for parameters in the direction of the peeling source,
        by including them in the predict"""
        
        if not self._peeling_Patch:
            self._peeling_Patch = []
            self._peeling_group = []
            for k in range(self.len()):
                patch = Meow.Patch(self._ns, self._sc_name[k],
                                   self._observation.phase_centre)
                self._peeling_Patch.append(patch)
                self._peeling_group.append([])
                for i in range(window):
                    if k+i<self.len():
                        self._peeling_Patch[k].add(self._skycomp[k+i])
                        self._peeling_group[k].append(self._sc_name[k+i])
        return True


    def make_peeling_Visset22 (self, window=1, array=None, observation=None):
        """Make Visset22 objects for the various peeling Patches.
        See .make_peeling_Patches()."""
        if not self._peeling_Visset22:                 # avoid duplication
            self.make_peeling_Patches(window=window)
            self._peeling_Visset22 = []
            for k in range(self.len()):
                vis = self.Patch2Visset22 (self._peeling_Patch[k], array=array,
                                           observation=observation,
                                           name=self._sc_name[k], visu=False)
                self._peeling_Visset22.append(vis)
        return True

    def peeling_Patch (self, index=0):
        """Return the specified (index) peeling Patch"""
        return self._peeling_Patch[index]

    def peeling_Visset22 (self, index=0):
        """Return the specified (index) peeling Visset22"""
        return self._peeling_Visset22[index]

    #---------------------------------------------------------------------------------
    
    def test (self):
        """Helper routine to add some test sources to the group"""
        # PointSource22.include_TDL_options('test')
        # PointSource22.include_TDL_options('test')
        self.add_PointSource('1st', 1,1)
        self.add_PointSource22('2nd', 1,0)
        self.add_PointSource22('3rd', 0,1)
        self.add_GaussianSource('4th', 1,1)
        return True




def include_SkyComponentGroup_TDL_options (prompt='definition'):
    """Instantiates meqbrouwser user options for the SkyComponentGroup class."""
    menuname = 'SkyComponentGroup22 ('+prompt+')'
    TDLCompileMenu(menuname,
                   TDLOption('TDL_peeling_group','size of peeling group',[1,2,3,4,5], more=int),
                   )
    return True
    









#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = [ns << 0.0]

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    observation = Meow.Observation(ns)
    Meow.Context.set (array, observation)

    scg = SkyComponentGroup22 (ns, name='test')
    scg.test()
    scg.display()
    # scg.skycomp(0).display()

    if True:
        vis = scg.Visset22(array, observation)
        vis.display()
        cc.append(vis.bundle())

    if True:
        scg.make_peeling_Visset22(3, array, observation)
        scg.display()
        for k in range(scg.len()):
            vis = scg.peeling_Visset22(k)
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


    if 1:
        scg = SkyComponentGroup22 (ns, name='testing')
        scg.test()
        scg.display('init')

        if 0:
            scg.translate(1,1)
            scg.display()
            scg.rotate(1)

        if 0:
            vis = scg.Visset22(array, observation)
            vis.display()

        if 0:
            scg.make_peeling_Patches(3)
            scg.display('peeling_Patches')

        if 1:
            scg.make_peeling_Visset22(3, array=array, observation=observation)
            scg.display('peeling_Visset22')


#=======================================================================
# Remarks:

#=======================================================================
