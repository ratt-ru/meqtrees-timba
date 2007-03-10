# file: ../Grunt/SkyComponentGroup22.py

# History:
# - 04feb2007: creation (from PointSource22.py) 

# Description:

# The SkyComponentGroup22 class represents a group of Meow SkyComponents.
# It is a virtual base class for a series of more specialized classes that
# represent various groups of SkyComponents (e.g. a grid for testing).
# It has various options for modifying its source pattern, e.g. rotation
# translation, magnification, etc.
# It is not a Meow Patch, but it can generate one. In addition, it can make
# a Visset22 with a ParmGroupManager, so we can solve for its source parameters
# in the Grunt system.
# It also has support for making subsets of its sources, for peeling. These
# can also be turned into Meow Patches and/or Grunt Visset22 objects.
 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import Joneset22
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

        # Deal with input arguments (default set by TDL_options):
        # (But they may also be set via **pp)
        self._pp = deepcopy(pp)
        if not isinstance(self._pp, dict): self._pp = dict()
        # self._pp.setdefault('peeling_group', TDL_peeling_group)

        # Each skycomp and its auxiliary info is in its own dict:
        self._skycomp = dict()
        self._order = []

        # Some placeholders:
        self._Patch = None
        self._Visset22 = None
        self._peeling_group = dict()
        self._peeling_Patch = dict()
        self._peeling_Visset22 = dict()

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
        ss += ' c='+str(self.flux_center())
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
        for key in self.order():
            sc = self._skycomp[key]
            s1 = ' wgt='+str(sc['wgt'])
            s1 += '   l='+str(sc['l'])+'   m='+str(sc['m'])
            print '  - '+key+': '+s1
        for key in self.order():
            sc = self._skycomp[key]
            print '  - '+key+': '+str(sc['skycomp'])
        print '** nominal SkyComponents ('+str(self.len())+'):'
        for key in self.order():
            sc = self._skycomp[key]
            print '  - '+key+': '+str(sc['nominal'])
        print '** Meow Patch: '+str(self._Patch)
        if self._Visset22:
            print '** Grunt Visset22: '+str(self._Visset22.oneliner())
        print '** Peeling support ('+str(len(self._peeling_Patch))+'):'
        if len(self._peeling_group)>0:
            for key in self.order():
                print '  - '+key+': '+str(self._peeling_group[key])
            for key in self.order():
                print '  - '+key+': '+str(self._peeling_Patch[key])
            if len(self._peeling_Visset22)>0:
                for key in self.order():
                    print '  - '+key+': '+str(self._peeling_Visset22[key].oneliner())
        print '** Optimum image size: '+str(self.imagesize())+' arcmin'
        print '**\n'
        return True

    #--------------------------------------------------------------------------

    def len(self):
        """Return the nr of sources in the group"""
        return len(self._skycomp)

    def order(self, order='descending'):
        """Return a list of skycomp names in the specified order"""
        return self._order

    def key(self, key=None):
        """Helper function to get a key into the skycomp dict"""
        if isinstance(key,int):
            # Convert an integer key (=index) into a string key:
            key = self.order()[key]
        if not isinstance(key,str):
            return False
        if key in self._skycomp.keys():
            return key
        return False

    def skycomp(self, key=None, nominal=False):
        """Return the specified (key) SkyComponent"""
        key = self.key(key)
        if nominal:
            return self._skycomp[key]['nominal']
        return self._skycomp[key]['skycomp']

    def add (self, skycomp, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a SkyComponent object to the group"""
        self._order.append(name)
        self._skycomp[name] = dict(skycomp=skycomp,
                                   nominal=skycomp,
                                   l=l, m=m, wgt=wgt)
        return self.len()

    #--------------------------------------------------------------------------

    def array (self, array=None):
        """Helper function to make sure of an (Meow) IfrArray object"""
        if not array:
            array = Meow.Context.get_array(None)
        return array

    def observation (self, observation=None):
        """Helper function to make sure of an (Meow) Observation object"""
        if not observation:
            observation = Meow.Context.get_observation(None)
        return observation

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
        self.get_parmgroups(skycomp)
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
        self.get_parmgroups(skycomp)
        return self.add(skycomp, name=name, l=l, m=m, wgt=wgt)


    def add_PointSource22 (self, name=None, l=0.0, m=0.0, wgt=1.0):
        """Add a Grunt PointSource22 object to the group"""
        # NB: Parameters are made for (l,m) with tag 'direction'
        direction = Meow.LMDirection(self._ns, name, l, m)
        skycomp = PointSource22.PointSource22(self._ns, name=name,
                                              direction=direction)
        self.get_parmgroups(skycomp)
        return self.add(skycomp, name=name, l=l, m=m, wgt=wgt)


    #--------------------------------------------------------------------------
    # Update its ParmGroupManager from the given skycomp:
    #--------------------------------------------------------------------------

    def get_parmgroups(self, skycomp, trace=True):
        """Helper function to get parmgroups from the skycomp"""
        # .......(not fully implemented yet)..........
        vis = skycomp.visibilities()
        vis_again = skycomp.visibilities()
        array = Meow.Context.get_array(None)
        vis0 = vis(*array.ifrs()[0])
        if trace:
            print '\n** get_parmgroups(): skycomp:',skycomp.name,' (vis0=',vis0,')'
        rr = dict()
        for tag in ['flux','direction','spectrum']:
            rr[tag] = vis0.search(tags=tag)
            if trace and len(rr[tag])==0:
                print '  -- vis0.search(tags=',tag,') -> rr[',tag,']=',rr[tag]
            for node in rr[tag]:
                if trace: print '  - tag=',tag,':',node.classname,node.name
        if trace: print
        return rr


    #--------------------------------------------------------------------------
    # Some operations on the skycomp (source) coordinates:
    # i.e. functions to rearrange the source pattern
    #--------------------------------------------------------------------------

    def rotate(self, angle=0.0):
        """Rotate the group (l,m) around (0,0) by an angle (rad)"""
        sina = math.sin(angle)
        cosa = math.cos(angle)
        for key in self.order():
            sc = self._skycomp[key]
            lnew = sc['l']*cosa - sc['m']*sina
            sc['m'] = sc['l']*sina + sc['m']*cosa
            sc['l'] = lnew
        return True


    def translate(self, dl=0.0, dm=0.0):
        """Translate the group (l,m) by the specified (dl,dm)"""
        for key in self.order():
            sc = self._skycomp[key]
            sc['l'] += dl
            sc['m'] += dm
        return True


    def magnify(self, ml=1.0, mm=1.0):
        """Magnify the group (l,m) w.r.t (0,0) by the specified factors (ml,mm)"""
        for key in self.order():
            sc = self._skycomp[key]
            sc['l'] *= ml
            sc['m'] *= mm
        return True


    def center(self):
        """Move the flux-center to (l=0,m=0)"""
        lm = self.flux_center()
        # print 'lm (before) =',lm 
        self.translate(dl=-lm[0], dm=-lm[1])
        lm = self.flux_center()
        # print 'lm (after) =',lm 
        return True


    def flux_center(self):
        """Calculate the coordinates (l,m) of the center-of-flux,
        i.e. the weighted sum of the skycomp coordinates (l,m)."""
        lc = 0.0
        mc = 0.0
        wtot = 0.0
        for key in self.order():
            sc = self._skycomp[key]
            wgt = 1.0
            lc += wgt*sc['l']
            mc += wgt*sc['m']
            wtot += wgt
        return [lc/wtot,mc/wtot]


    #--------------------------------------------------------------------------
    # Corruption:
    #--------------------------------------------------------------------------

    def corrupt (self, jones, label='G', key=None):
        """Corrupt the specified (key) SkyComponent with the given Jones matrix.
        If key==None, assume an image-plane (overall) Jones matrix (like EJones)"""

        if key==None:
            # Image-plane effect: not yet implemented....
            return False
        else:
            key = self.key(key)
            sc = self._skycomp[key]['skycomp']
            # Alternative: sc = sc.corrupt(station_jones=jones.matrixet())
            sc = Meow.CorruptComponent(self._ns, sc, label,
                                       station_jones=jones.matrixet())
            self._skycomp[key]['skycomp'] = sc
        return True



    #--------------------------------------------------------------------------
    # Make visibilities (via the Meow Patch)
    #--------------------------------------------------------------------------

    def Visset22 (self, array=None, observation=None, name=None,
                  visu=True, nominal=False):
        """Create a Visset22 object from the visibilities of this SkyComponentGroup22.
        If nominal==True, use the nominal (uncorrupted) skycomps."""
        if not self._Visset22:                               # avoid duplication
            self.Meow_Patch(observation, nominal=nominal)    # make sure of self._Patch
            self._Visset22 = self.Patch2Visset22 (self._Patch, array=array,
                                                  name=name, visu=visu)
        return self._Visset22


    def Patch2Visset22 (self, Patch, array=None, observation=None,
                        name=None, visu=True):
        """Helper function to create a Grunt Visset22 object from the given Meow Patch"""

        if not name: name = self._name
        observation = self.observation(observation)
        array = self.array(array)

        polrep = 'linear'
        if observation.circular():
            polrep = 'circular'

        # Make the Visset22:
        vis = Visset22.Visset22 (self._ns, quals=[], label=name,
                                 polrep=polrep, array=array)
        # Make the 2x2 visibility matrices per ifr:
        matrixet = Patch.visibilities(array, observation)
        vis.matrixet(new=matrixet)

        # ParmGroupManager... (get all MeqParms from self.ns...?)

        if visu: vis.visualize('SkyComponentGroup22')
        return vis

    def visibilities (self, array=None, observation=None, nominal=False):
        """Return 'Meow' visibilities, i.e. as an unqualified node.
        If nominal==True, use the nominal (uncorrupted) skycomps."""
        self.Meow_Patch(observation, nominal=nominal)
        return self._Patch.visibilities(array,observation)


    def Meow_Patch (self, observation=None, nominal=False):
        """Generate a single Meow Patch from the skycomps in this group.
        If nominal==True, use the nominal (uncorrupted) skycomps."""
        if not self._Patch:
            observation = self.observation(observation)
            self._Patch = Meow.Patch(self._ns, self._name,
                                     observation.phase_centre)
            for key in self.order():
                if nominal:
                    self._Patch.add(self._skycomp[key]['nominal'])
                else:
                    self._Patch.add(self._skycomp[key]['skycomp'])
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
            self._peeling_Patch = dict()
            self._peeling_group = dict()
            for k in range(self.len()):
                key = self.key(k)
                patch = Meow.Patch(self._ns, key, self.observation().phase_centre)
                self._peeling_Patch[key] = patch
                self._peeling_group[key] = []
                for i in range(window):
                    if k+i<self.len():
                        key1 = self.key(k+i)
                        self._peeling_Patch[key].add(self._skycomp[key1]['skycomp'])
                        self._peeling_group[key].append(key1)
        return True


    def make_peeling_Visset22 (self, window=1, array=None, observation=None):
        """Make Visset22 objects for the various peeling Patches.
        See .make_peeling_Patches()."""
        if not self._peeling_Visset22:                 # avoid duplication
            self.make_peeling_Patches(window=window)
            self._peeling_Visset22 = dict()
            for key in self.order():
                vis = self.Patch2Visset22 (self._peeling_Patch[key],
                                           array=array,
                                           observation=observation,
                                           name=key, visu=False)
                self._peeling_Visset22[key] = vis
        return True


    def peeling_Patch (self, key=0):
        """Return the specified (key) peeling Patch"""
        key = self.key(key)
        return self._peeling_Patch[key]


    def peeling_Visset22 (self, key=0):
        """Return the specified (key) peeling Visset22"""
        key = self.key(key)
        return self._peeling_Visset22[key]

    #---------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------
    
    def test (self):
        """Helper routine to add some test sources to the group"""
        self.add_PointSource('1st', 1,1)
        self.add_PointSource22('2nd', 1,0)
        self.add_PointSource22('3rd', 0,1)
        self.add_GaussianSource('4th', 1,-1)
        return True


#========================================================================================

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

    cc = []

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
        jones = Joneset22.GJones(ns, quals='xxx', stations=ANTENNAS, simulate=True)
        scg.corrupt(jones, label='G', key=1)
        scg.display('corrupted')

    if True:
        vis = scg.Visset22()
        vis.display()
        cc.append(vis.bundle())

    if False:
        scg.make_peeling_Visset22(window=3)
        scg.display()
        for k in range(scg.len()):
            vis = scg.peeling_Visset22(k)
            vis.display()
            cc.append(vis.bundle())

    if len(cc)==0: cc = [ns << 0.0]
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
        num_stations = 5
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        Meow.Context.set (array, observation)


    if 1:
        scg = SkyComponentGroup22 (ns, name='testing')
        scg.test()
        scg.display('init')

        if 1:
            # scg.rotate(0.01)
            # scg.translate(1,10)
            # scg.magnify(2,0.5)
            scg.center()
            scg.display()

        if 0:
            jones = Joneset22.GJones(ns, quals='xxx', stations=ANTENNAS, simulate=True)
            scg.corrupt(jones, label='G', key=3)
            scg.display()

        if 0:
            vis = scg.Visset22(array)
            vis.display()
            scg.display('Visset22')

        if 0:
            scg.make_peeling_Patches(window=3)
            scg.display('peeling_Patches')

        if 0:
            scg.make_peeling_Visset22(window=2)
            scg.display('peeling_Visset22')


#=======================================================================
# Remarks:

#=======================================================================
