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

TDL_options_counter = 0

# Global counter used to generate unique node-names
# unique = -1


#======================================================================================


def include_TDL_options(prompt='definition'):
    """Instantiates user options for the meqbrouwser"""
    global TDL_options_counter
    if TDL_options_counter==0:
        predefined = ['unpol','Q','U','V','QU','QUV','UV','QV']
        predefined.extend(['3c147','3c286'])
        predefined.append(None)
        menuname = 'PointSource22 ('+prompt+')'
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
        TDL_options_counter += 1
    return True


#======================================================================================

class PointSource22 (Meow.PointSource):
    """A Meow.PointSource with some extra features"""

    def __init__(self, ns, direction=None,
                 parm_options=record(node_groups='Parm'),
                 simulate=False, **pp):

        include_TDL_options()

        # Deal with input parameters:
        self._pp = pp
        if not isinstance(self._pp, dict): self._pp = dict()
        self._pp.setdefault('predefined', TDL_predefined)
        self._pp.setdefault('I', TDL_StokesI)
        self._pp.setdefault('Q', TDL_StokesQ)
        self._pp.setdefault('U', TDL_StokesU)
        self._pp.setdefault('V', TDL_StokesV)
        self._pp.setdefault('spi', TDL_spi)
        self._pp.setdefault('freq0', TDL_freq0)
        self._pp.setdefault('RM', TDL_RM)
        self._pp.setdefault('name', TDL_source_name)

        # Some non-Meow attributes
        self._simulate = simulate

        # Make a predefined source, if required:
        self.predefine(self._pp)

        # Used for .oneliner() and .display():
        self._IQUV = [self._pp['I'],self._pp['Q'],self._pp['U'],self._pp['V']]

        # The source direction is kept in Meow.PointSource (self.direction):
        if direction==None:
            direction = Meow.LMDirection(ns, self._pp['name'], l=0.0, m=0.0)

        # Initialise its Meow counterpart:
        Meow.PointSource.__init__(self, ns=ns, name=self._pp['name'],
                                  I=self._pp['I'], Q=self._pp['Q'],
                                  U=self._pp['U'], V=self._pp['V'],
                                  spi=self._pp['spi'], freq0=self._pp['freq0'],
                                  RM=self._pp['RM'],
                                  direction=direction)

        # Create a Grunt ParmGroupManager object:
        # NB: Parameters have been made (by LMDirection) for (l,m) with tag 'direction'
        # NB: Parameters have been made for I with tag 'flux'
        # NB: Parameters have been made for Q,U,V with tag 'flux pol'
        # NB: Parameters have been made for si with tag 'spectrum'
        # NB: Parameters have been made for RM with tag 'pol'
        self._pgm = ParmGroupManager.ParmGroupManager(ns, label=self._pp['name'])

        # Some placeholders:
        self._Visset22 = None

        # Finished:
        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self._pp['name'])
        ss += '  '+str(self._pp['predefined'])
        ss += '  '+str(self._IQUV)
        if self._pp['spi']:
            ss += '  (spi='+str(self._pp['spi'])+')'
        if self._pp['freq0']:
            ss += '  (f0='+str(self._pp['freq0'])+')'
        if self._pp['RM']:
            ss += '  (RM='+str(self._pp['RM'])+')'
        return ss


    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        for key in self._pp.keys():
            print '  - pp['+key+'] = '+str(self._pp[key])
        print '**\n'
        return True

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def predefine(self, pp):
        """Modify the parameters in pp if a predefined source has been spefiied"""
        # A small number of predefined sources is available:

        if not isinstance(pp['predefined'], str):
            return True                        # not required

        self._pp['name'] += '_'+str(pp['predefined'])

        if (pp['predefined']=='unpol'):
            pp['I'] = 1.0
        elif (pp['predefined']=='unpol2'):
            pp['I'] = 2.0
        elif (pp['predefined']=='unpol10'):
            pp['I'] = 10.0
        elif (pp['predefined']=='Qonly'):
            pp['Q'] = 0.1
        elif (pp['predefined']=='Uonly'):
            pp['U'] = -0.1
        elif (pp['predefined']=='Vonly'):
            pp['V'] = 0.02                            
        elif (pp['predefined']=='QU'):
            pp['Q'] = 0.1
            pp['U'] = -0.1
        elif (pp['predefined']=='QUV'):
            pp['Q'] = 0.1
            pp['U'] = -0.1
            pp['V'] = 0.02
        elif (pp['predefined']=='D1'):          # D1.MS 
            pp['I'] = 11.0
            pp['Q'] = 0.1
            pp['U'] = -0.1
            RA = 1.49488454017
            Dec = 0.870081695897
        elif (pp['predefined']=='QU2'):
            pp['I'] = 2.0
            pp['Q'] = 0.4
            pp['U'] = -0.3
        elif (pp['predefined']=='RMtest'):
            RM = 1.0
            pp['Q'] = 0.1
            pp['U'] = -0.1
        elif (pp['predefined']=='SItest'):
            pp['spi'] = -0.7
            
            # The following are not yet implemented:
            # (vector SI are not yet supported by Meow)
        elif True:
            raise ValueError,'predefined not recognised: '+str(pp['predefined'])

        elif (pp['predefined']=='I0polc'):
            I0 = array([[2,-.3,.1],[.3,-.1,0.03]]),
        elif pp['predefined']=='3c147':
            I0 = 10**1.766
            pp['SI'] = [0.447, -0.184]
        elif (pp['predefined']=='3c48'):
            I0 = 10**2.345
            pp['SI'] = [0.071, -0.138]
        elif (pp['predefined']=='3c286'): 
            I0 = 10**1.48
            pp['SI'] = [0.292, -0.124]
            # pp['Q'] = [2.735732, -0.923091, 0.073638]         # <-----
            # pp['U'] = [6.118902, -2.05799, 0.163173]          # <-----
        elif (pp['predefined']=='3c295'):
            I0 = 10**1.485
            pp['SI'] = [0.759, -0.255]
            
        elif True:
            raise ValueError,'predefined not recognised: '+str(pp['predefined'])

        return True


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def Visset22 (self, array, observation, name=None, phase_centre=None, visu=False):
        """Create a Visset22 object from the visibilities generated by this PointSource22"""
        if not self._Visset22:                   # avoid duplication
            polrep = 'linear'
            if observation.circular():
                polrep = 'circular'
            # Make the Visset22:
            # NB: Use the ORIGINAL nodescope (self.ns0), not the Qualscope (self.ns)
            #     See Meow.Parametrization.py
            if not name: name = self._pp['name']
            self._Visset22 = Visset22.Visset22 (self.ns0, quals=[], label=name,
                                                polrep=polrep,
                                                # observation=observation,
                                                array=array)
            # Make the 2x2 visibility matrices per ifr:
            if False:
                # Use this if the source has to be shifted (KJones):
                matrixet = self.visibilities(array,observation)
                self._Visset22.matrixet(new=matrixet)
            else:
                # Use this if the source is in the phase centre (no KJones):
                matrix = self.coherency(observation)
                self._Visset22.fill_with_identical_matrices ('PS22_visibility', coh=matrix)

            # ParmGroupManager... (get all MeqParms from self.ns...?)
            # NB: Not if self._simulate==True (i.e. hide the MeqParms)

            if phase_centre:
                # If a Direction object is given, shift the phase centre of the uv-data
                # to its position (l,m).
                self._Visset22.shift_phase_centre(phase_centre, 'Visset22')

            if visu: self._Visset22.visualize('PointSource22')
        return self._Visset22






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
    Meow.Context.set (array, observation)
    direction = Meow.LMDirection(ns, 'xxx', l=1.0, m=1.0)
    # direction = Meow.LMDirection(ns, TDL_source_name, l=1.0, m=1.0)
    ps = PointSource22 (ns, direction=direction)
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
        # ps = PointSource22 (ns, predefined=src, direction=direction)
        ps = PointSource22 (ns, predefined=src)
        ps.display()

    if 1:
        vis = ps.Visset22(array, observation)
        vis.display()


#=======================================================================
# Remarks:

#=======================================================================
