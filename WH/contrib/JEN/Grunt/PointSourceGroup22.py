# file: ../Grunt/PointSourceGroup22.py

# History:
# - 04feb2007: creation (from SkyComponentGroup22.py) 

# Description:

# Various specialised SkyComponentGroup classes that contain groups of
# point sources in various patterns, for testing.
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

  

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

# from Timba.Contrib.JEN.Grunt import Visset22
# from Timba.Contrib.JEN.Grunt import ParmGroupManager
from Timba.Contrib.JEN.Grunt import PointSource22
from Timba.Contrib.JEN.Grunt import SkyComponentGroup22

import math
import random
from copy import deepcopy


# Global counter used to generate unique node-names
# unique = -1



#======================================================================================
#======================================================================================


def include_EqualPointSourceGrid_TDL_options (prompt='definition'):
    """Instantiates meqbrouwser user options for the EqualPointSourceGrid class."""
    menuname = 'EqualPointSourceGrid22 ('+prompt+')'
    TDLCompileMenu(menuname,
                   TDLOption('TDL_pattern','source pattern',
                             ['grid','cross','star8'], more=str),
                   TDLOption('TDL_nsrc2','nsrc2 (-nsrc2:nsrc2)',[1,2,3,4,0], more=int),
                   TDLOption('TDL_l0','l0 (arcmin)',[0.0,5,10,20,40,80], more=float),
                   TDLOption('TDL_m0','m0 (arcmin)',[0.0,5,10,20,40,80], more=float),
                   TDLOption('TDL_dl','dl (arcmin)',[5.0,10,20,40,80], more=float),
                   TDLOption('TDL_dm','dm (arcmin)',[5.0,10,20,40,80], more=float),
                   TDLOption('TDL_fluxfactor','flux-attenn. factor',[1.0, 0.7, 0.5], more=float),
                   )
    # Also include the source definition options:
    PointSource22.include_TDL_options(prompt+': sources')
    return True
    



class EqualPointSourceGrid22 (SkyComponentGroup22.SkyComponentGroup22):
    """A SkyComponentGroup22 with a pattern of point-sources of the same type, for testing."""

    def __init__(self, ns, name='epsg22', **pp):

        # Initialise its Meow counterpart:
        SkyComponentGroup22.SkyComponentGroup22.__init__(self, ns=ns, name=name)

        # Deal with input arguments (default set by TDL_options):
        # (But they may also be set via **pp)
        self._pp = deepcopy(pp)
        if not isinstance(self._pp, dict): self._pp = dict()
        self._pp.setdefault('pattern', TDL_pattern)
        self._pp.setdefault('nsrc2', TDL_nsrc2)
        self._pp.setdefault('l0', TDL_l0)
        self._pp.setdefault('m0', TDL_m0)
        self._pp.setdefault('dl', TDL_dl)
        self._pp.setdefault('dm', TDL_dm)
        self._pp.setdefault('fluxfactor', TDL_fluxfactor)
        print 'self_pp=',self._pp

        # Call the specified function:
        DEG = math.pi/180.
        ARCMIN = DEG/60
        self.make_sources(pattern=self._pp['pattern'],
                          basename='S',
                          l0=self._pp['l0'],
                          m0=self._pp['m0'],
                          dl=self._pp['dl']*ARCMIN,
                          dm=self._pp['dm']*ARCMIN,
                          nsrc2=self._pp['nsrc2'],
                          fluxfactor=self._pp['fluxfactor'])

        # Finished:
        return None

    #----------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = SkyComponentGroup22.SkyComponentGroup22.oneliner(self)
        ss += '  '+str(self._pp['pattern'])+'_'+str(self._pp['nsrc2'])
        return ss

    #----------------------------------------------------------------------

    def imagesize (self):
        """Returns the optimum image size, based on grid parameters."""
        # return grid_size*grid_step;
        return max(self._pp['dl'],self._pp['dm'])*self._pp['nsrc2']       # in arcmin.....!!?          



    #----------------------------------------------------------------------

    def make_sources (self, pattern, basename,l0,m0,dl,dm,nsrc2,
                      fluxfactor=1.0):
        """Returns sources arranged in the specified pattern"""

        # The sources flux is multiplied by fluxfactor for each source.
        # This is to generate some flux-variation (if fluxfactor != 1.0)
        flux = 1.0
        
        if pattern=='grid':
            # Returns sources arranged in a grid
            self.add_PointSource22(name=basename+"+0+0",l=l0,m=m0)
            for dx in range(-nsrc2,nsrc2+1):
                for dy in range(-nsrc2,nsrc2+1):
                    if dx or dy:
                        flux *= fluxfactor
                        name = "%s%+d%+d" % (basename,dx,dy)
                        self.add_PointSource22(name=name,l=l0+dl*dx,
                                               m=m0+dm*dy, flux=flux)
                        
        elif pattern=='cross':
            # Returns sources arranged in a cross
            self.add_PointSource22(name=basename+"+0+0",l=l0,m=m0)
            dy = 0;
            for dx in range(-nsrc2,nsrc2+1):
                if dx:
                    flux *= fluxfactor
                    name = "%s%+d%+d" % (basename,dx,dy);
                    self.add_PointSource22(name=name,l=l0+dl*dx,
                                           m=m0+dm*dy, flux=flux)
            dx = 0;
            for dy in range(-nsrc2,nsrc2+1):
                if dy:
                    flux *= fluxfactor
                    name = "%s%+d%+d" % (basename,dx,dy);
                    self.add_PointSource22(name=name,l=l0+dl*dx,
                                           m=m0+dm*dy, flux=flux)

        elif pattern=='star8':
            # Returns sources arranged in an 8-armed star
            self.add_PointSource22(name=basename+"+0+0",l=l0,m=m0)
            for n in range(1,nsrc2+1):
                for dx in (-n,0,n):
                    for dy in (-n,0,n):
                        if dx or dy:
                            flux *= fluxfactor
                            name = "%s%+d%+d" % (basename,dx,dy)
                            self.add_PointSource22(name=name,l=l0+dl*dx,
                                                   m=m0+dm*dy, flux=flux)

        # Finished:
        return True





#===============================================================
# Test routine (with meqbrowser):
#===============================================================

# include_EqualPointSourceGrid_TDL_options('test')

def _define_forest(ns):

    cc = [ns << 0.0]

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    observation = Meow.Observation(ns)
    Meow.Context.set (array, observation)

    epsg = EqualPointSourceGrid22 (ns, name='test')
    epsg.display()
    epsg.skycomp(0).display()

    if True:
        vis = epsg.Visset22()
        vis.addGaussianNoise(0.1, visu=True)
        vis.display()
        cc.append(vis.bundle())

    if True:
        epsg.make_peeling_Visset22(window=3)
        epsg.display()
        for k in range(epsg.len()):
            vis = epsg.peeling_Visset22(k)
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

    include_EqualPointSourceGrid_TDL_options('test')

    if 1:
        num_stations = 3
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        Meow.Context.set (array, observation)

    if 1:
        epsg = EqualPointSourceGrid22 (ns, name='testing', fluxfactor=0.5)
        epsg.display()

        if 1:
            epsg.make_peeling_Patches(window=5)
            epsg.display('peeling_Patches')

        if 0:
            epsg.make_peeling_Visset22(window=3)
            epsg.display('peeling_Visset22')


#=======================================================================
# Remarks:

#=======================================================================
