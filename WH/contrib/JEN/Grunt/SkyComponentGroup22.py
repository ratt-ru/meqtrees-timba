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


# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

class SkyComponentGroup22 (object):
    """Virtual base class for specialised groups of SkyComponents"""

    def __init__(self, ns, name='SkyComponentGroup22'):

        self._ns = ns
        self._name = name
        self._observation = Meow.Context.get_observation(None)    # ....??

        self._skycomp = []
        self._sc_name = []
        self._ll = []
        self._mm = []
        self._wgt = []
        # self._unit = 'arcmin'

        # Some placeholders:
        self._Patch = None
        self._Visset22 = None
        self._peeling_patch = []
        self._peeling_group = []

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
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+str(sc)
        for k in range(self.len()):
            s1 = ' l='+str(self._ll[k])+' m='+str(self._mm[k])+' wgt='+str(self._wgt[k])
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+s1
        print '** Peeling patches ('+str(len(self._peeling_patch))+'):'
        for k,pp in enumerate(self._peeling_patch):
            print '  - '+str(k)+': '+str(self._sc_name[k])+': '+str(self._peeling_group[k])
        print '**\n'
        return True

    #--------------------------------------------------------------------------

    def len(self):
        """Return the nr of sources in the group"""
        return len(self._skycomp)

    def add (self, skycomp, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a SkyComponent object to the group"""
        self._skycomp.append(skycomp)
        self._sc_name.append(name)
        self._ll.append(l)
        self._mm.append(m)
        self._wgt.append(wgt)
        return self.len()

    #--------------------------------------------------------------------------

    def add_PointSource (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Meow PointSource object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        sc_dir = Meow.LMDirection(self._ns, name, l, m)
        skycomp = Meow.PointSource(self._ns, name, sc_dir)
        return self.add(skycomp, name=name, l=l, m=m, wgt=wgt)


    def add_PointSource22 (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Grunt PointSource22 object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        sc_dir = Meow.LMDirection(self._ns, name, l, m)
        skycomp = PointSource22.PointSource22(self._ns, name=name, direction=sc_dir)
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

    def make_peeling_patches (self, window=1, trace=True):
        """A peeling patch contains the source itself, and also a small number
        of (next) fainter sources. The idea is to reduce contamination by those
        fainter sources by including them in the predict when solving for
        parameters in the direction of the peeling source.""" 
        if not self._peeling_patch:
            if trace: print '\n** make_peeling_patches(',window,'):'
            self._peeling_patch = []
            self._peeling_patch = []
            self._peeling_group = []
            for k in range(self.len()):
                self._peeling_patch.append(Meow.Patch(self._ns, self._sc_name[k],
                                                      self._observation.phase_centre))
                self._peeling_group.append([])
                if trace: print '- peeling_patch:',k,self._sc_name[k]
                for i in range(window):
                    if k+i<self.len():
                        self._peeling_patch[k].add(self._skycomp[k+i])
                        self._peeling_group[k].append(self._sc_name[k+i])
                        if trace: print '  -- include skycomp:',i,self._sc_name[k+i]
            if trace: print
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
        # PointSource22.include_TDL_options('test')
        # PointSource22.include_TDL_options('test')
        scg.add_PointSource('first', 1,1)
        scg.add_PointSource22('second', 1,0)
        scg.add_PointSource22('third', 0,1)
        return True










#======================================================================================
#======================================================================================

class PointSourceGroup22 (SkyComponentGroup22):
    """A SkyComponentGroup22 with a pattern of point-sources of the same type, for testing.
    This is a virtual base-class for a range of more specific source patterns."""

    def __init__(self, ns, name='PointSourceGroup22', **pp):

        self.include_TDL_options()

        # Initialise its Meow counterpart:
        SkyComponentGroup22.__init__(self, ns=ns, name=name)

        # Finished:
        return None


    def include_TDL_options (self, prompt='definition'):
        """Instantiates user options for the meqbrouwser.
        Re-implementation of the base class function. Include the TDL options
        for a PointSource22 object."""
        menuname = 'PointSourceGroup22 ('+prompt+')'
        TDLCompileMenu(menuname,
                       TDLOption('TDL_xxx',"xxx",[1,2,3], more=int),
                       TDLOption('TDL_yyy',"yyy",[1,2,3], more=int),
                       )
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
        scg = SkyComponentGroup22 (ns, name='testing')
        scg.test()
        scg.display('init')

    if 1:
        scg.make_peeling_patches(2)
        scg.display('peeling_patches')

    if 0:
        scg.translate(1,1)
        scg.display()
        scg.rotate(1)

    if 0:
        vis = scg.Visset22(array, observation)
        vis.display()


#=======================================================================
# Remarks:

#=======================================================================
