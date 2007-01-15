# file: ../Grunt/PointSource22.py

# History:
# - 15jan2007: creation 

# Description:

# The PointSource22 class is a wrapper around the Meow PointSource class.
# Its extra features are:
# - It has a number of predefined sources (3c147 etc) 
# - It makes a Visset22 with a ParmGroupManager, so we can solve for
#   source parameters in the Grunt system

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import ParmGroupManager
# from Timba.Contrib.JEN.Grunt import Joneset22

# from Timba.Contrib.JEN.util import JEN_bookmarks
# from Timba.Contrib.JEN import MG_JEN_dataCollect

# from copy import deepcopy




# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

def include_TDL_options(menuname="PointSource22 definition"):
    """Instantiates user options for the meqbrouwser"""
    predefined = ['unpol','Q','U','V','QU','QUV','UV','QV']
    predefined.extend(['3c147','3c286'])
    predefined.append(None)
    TDLCompileMenu(menuname,
                   TDLOption('TDL_source_name',"source name (overridden by predefined)", ['PS22'], more=str),
                   TDLOption('TDL_predefined',"predefined source",predefined),
                   TDLOption('TDL_StokesI',"Stokes I (Jy)",[1.0,2.0,10.0], more=float),
                   TDLOption('TDL_StokesQ',"Stokes Q (Jy)",[None, 0.0, 0.1], more=float),
                   TDLOption('TDL_StokesU',"Stokes U (Jy)",[None, 0.0, -0.1], more=float),
                   TDLOption('TDL_StokesV',"Stokes V (Jy)",[None, 0.0, 0.02], more=float),
                   TDLOption('TDL_spi',"Spectral Index (I=I0*(f/f0)**(-spi)",[0.0, 1.0], more=float),
                   TDLOption('TDL_freq0',"Reference freq (MHz) for Spectral Index",[None, 1.0], more=float),
                   TDLOption('TDL_RM',"Intrinsic Rotation Measure (rad/m2)",[None, 0.0, 1.0], more=float),
                   );
    return True

#======================================================================================

class PointSource22 (Meow.PointSource):
    """A Meow.PointSource with some extra features"""

    def __init__(self, ns, name='<ps>', direction=None,
                 I=1.0, Q=None, U=None, V=None,
                 Iorder=0, Qorder=0, Uorder=0, Vorder=0,
                 spi=0.0, freq0=None, RM=None,
                 parm_options=record(node_groups='Parm'),
                 predefined=None, simulate=False):

        # Some non-Meow attributes
        self._name = name
        self._predefined = predefined
        self._simulate = simulate

        # A small number of predefined sources is available:
        if isinstance(predefined, str):
            self._name = predefined
            if (predefined=='unpol'):
                I = 1.0
            elif (predefined=='unpol2'):
                I = 2.0
            elif (predefined=='unpol10'):
                I = 10.0
            elif (predefined=='Qonly'):
                Q = 0.1
            elif (predefined=='Uonly'):
                U = -0.1
            elif (predefined=='Vonly'):
                V = 0.02                            
            elif (predefined=='QU'):
                Q = 0.1
                U = -0.1
            elif (predefined=='QUV'):
                Q = 0.1
                U = -0.1
                V = 0.02
            elif (predefined=='D1'):          # D1.MS 
                I = 11.0
                Q = 0.1
                U = -0.1
                RA = 1.49488454017
                Dec = 0.870081695897
            elif (predefined=='QU2'):
                I = 2.0
                Q = 0.4
                U = -0.3
            elif (predefined=='RMtest'):
                RM = 1.0
                Q = 0.1
                U = -0.1
            elif (predefined=='SItest'):
                spi = -0.7

            # The following are not yet implemented:
            # (vector SI are not yet supported by Meow)
            elif True:
                raise ValueError,'predefined not recognised: '+str(predefined)
            elif (predefined=='I0polc'):
                I0 = array([[2,-.3,.1],[.3,-.1,0.03]]),
            elif predefined=='3c147':
                I0 = 10**1.766
                SI = [0.447, -0.184]
            elif (predefined=='3c48'):
                I0 = 10**2.345
                SI = [0.071, -0.138]
            elif (predefined=='3c286'): 
                I0 = 10**1.48
                SI = [0.292, -0.124]
                # Q = [2.735732, -0.923091, 0.073638]         # <-----
                # U = [6.118902, -2.05799, 0.163173]          # <-----
            elif (predefined=='3c295'):
                I0 = 10**1.485
                SI = [0.759, -0.255]

            elif True:
                raise ValueError,'predefined not recognised: '+str(predefined)

        # Initialise its Meow counterpart:
        self._IQUV = [I,Q,U,V]
        self._spi = spi
        Meow.PointSource.__init__(self, ns=ns, name=self._name,
                                  I=I, Q=Q, U=U, V=V,
                                  Iorder=Iorder, Qorder=Qorder,
                                  Uorder=Uorder, Vorder=Vorder,
                                  spi=spi, freq0=freq0, RM=RM,
                                  direction=direction,
                                  parm_options=parm_options)

        # Create a Grunt ParmGroupManager object:
        self._pgm = ParmGroupManager.ParmGroupManager(ns, label=name,
                                                      # quals=self.quals(),
                                                      simulate=self._simulate)
        # Some placeholders:
        self._Visset22 = None

        # Finished:
        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self._name)
        ss += '  '+str(self._predefined)
        ss += '  '+str(self._IQUV)
        if self._spi:
            ss += '  (spi='+str(self._spi)+')'
        if self._freq0:
            ss += '  (f0='+str(self._freq0)+')'
        if self._rm:
            ss += '  (RM='+str(self._rm)+')'
        return ss


    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print '**\n'
        return True


    #--------------------------------------------------------------------------


    def Visset22 (self, array, observation, visu=False):
        """Create a Visset22 object from the visibilities generated
        by this PointSource"""
        if not self._Visset22:                   # avoid duplication
            polrep = 'linear'
            if observation.circular():
                polrep = 'circular'
            # Make the Visset22:
            # NB: Use the ORIGINAL nodescope (self.ns0), not the Qualscope (self.ns)
            #     See Meow.Parametrization.py
            self._Visset22 = Visset22.Visset22 (self.ns0, quals=[], label=self._name,
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

            if visu: self._Visset22.visualize('PointSource22')
        return self._Visset22






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

# include_TDL_options()

def _define_forest(ns):

    cc = []

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    observation = Meow.Observation(ns)
    direction = Meow.LMDirection(ns, TDL_source_name, l=1.0, m=1.0)
    ps = PointSource22 (ns, name=TDL_source_name, predefined=TDL_predefined,
                        I=TDL_StokesI, Q=TDL_StokesQ,
                        U=TDL_StokesU, V=TDL_StokesV,
                        spi=TDL_spi, freq0=TDL_freq0, RM=TDL_RM,
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
        src = 'unpol'
        src = 'QUV'
        direction = Meow.LMDirection(ns, src, l=1.0, m=1.0)
        ps = PointSource22 (ns,predefined=src, direction=direction)
        ps.display()

    if 1:
        vis = ps.Visset22(array, observation)
        vis.display()


#=======================================================================
# Remarks:

#=======================================================================
