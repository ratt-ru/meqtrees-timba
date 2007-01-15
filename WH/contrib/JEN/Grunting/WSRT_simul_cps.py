# file: ../contrib/JEN/Grunt/WSRT_simul_cps.py

# Description:
# Inspect the data in a Measurement Set in various ways.
# The data is NOT written back.

# History:
# - 14jan2007: creation

# Copyright: The MeqTree Foundation

#========================================================================
# Preamble:
#========================================================================

from Timba.TDL import *
from Timba.Meq import meq
# import math

import Meow
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..
from Timba.Contrib.JEN.Grunting import WSRT_Jones

# import Grunt
from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.Grunt import PointSource22


#========================================================================
# meqbrowser user menu-items:
#========================================================================

# Run-time menu:
JEN_Meow_Utils.include_ms_options(has_input=False, has_output='MODEL_DATA',
                                  tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();


# Compile-time menu:
# PointSource22.include_TDL_options('Central Point Source (cps)')   #............??
menuname = 'Central Point Source (cps)'
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

joneseq = ['G','GD','D','GDF','J','E','B']
TDLCompileMenu('WSRT_Jones (corruption)',
               TDLOption('TDL_joneseq', 'sequence of Jones matrices', joneseq, more=str),
               TDLOption('TDL_D_coupled_dang',"D: coupled (dangX=dangY)", [True, False]),
               TDLOption('TDL_D_coupled_dell',"D: coupled (dellX=-dellY)", [True, False]),
               TDLOption('TDL_J_diagonal',"J: diagonal matrix", [False, True]),
               );

TDLCompileOption('TDL_num_stations',"Number of stations",[5,27,14,3,4,5,6,7,8,9,10], more=int);
TDLCompileOption('TDL_display_Visset22',"Display the Visset22 object", [True,False]);
TDLCompileOption('TDL_cache_policy',"Node result caching policy",[100,0], more=int);




#========================================================================
# Tree definition:
#========================================================================

def _define_forest (ns):
    """Inspect the contents of the MS"""

    array = Meow.IfrArray(ns, range(1,TDL_num_stations+1))
    observation = Meow.Observation(ns)
    direction = Meow.LMDirection(ns, TDL_source_name, l=0.0, m=0.0)
    ps = PointSource22.PointSource22 (ns, name=TDL_source_name,
                                      predefined=TDL_predefined,
                                      I=TDL_StokesI, Q=TDL_StokesQ,
                                      U=TDL_StokesU, V=TDL_StokesV,
                                      spi=TDL_spi, freq0=TDL_freq0, RM=TDL_RM,
                                      direction=direction)
    ps.display()
    vis = ps.Visset22(array, observation, visu=True)

    # Corrupt (WSRT_Jones, noise)
    jseq = []
    for c in TDL_joneseq:
        if c=='G':
            jseq.append(WSRT_Jones.GJones(ns, stations=array.stations(),
                                          simulate=True))
        elif c=='D':
            jseq.append(WSRT_Jones.DJones(ns, stations=array.stations(),
                                          coupled_dell=TDL_D_coupled_dell,
                                          coupled_dang=TDL_D_coupled_dang,
                                          simulate=True))
        elif c=='F':
            jseq.append(WSRT_Jones.FJones(ns, stations=array.stations(),
                                          simulate=True))
        elif c=='J':
            jseq.append(WSRT_Jones.JJones(ns, stations=array.stations(),
                                          diagonal=TDL_J_diagonal,
                                          simulate=True))
        elif c=='E':
            jseq.append(WSRT_Jones.EJones(ns, stations=array.stations(),
                                          simulate=True))
        elif c=='B':
            jseq.append(WSRT_Jones.BJones(ns, stations=array.stations(),
                                          simulate=True))
        else:
            raise ValueError,'WSRT jones matrix not recognised: '+str(c)

    if len(jseq)>0:
        jones = Joneset22.Joneseq22(jseq)
        vis.corrupt(jones, visu=True)

    # Finished:
    if TDL_display_Visset22:
        vis.display(full=True)
    vis.make_sinks(vdm='vdm')
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_WSRT_simul_cps (mqs,parent):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    req = JEN_Meow_Utils.create_io_request(override_output_column='MODEL_DATA');
    mqs.execute('vdm',req,wait=False);
    return True
                                     
  
def _tdl_job_2_make_image (mqs,parent):
    JEN_Meow_Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);
    return True



#========================================================================
# Test routine (without the meqbrowser):
#========================================================================

if __name__ == '__main__':
    ns = NodeScope();
    _define_forest(ns);
    # resolves nodes
    ns.Resolve();  
    print len(ns.AllNodes()),'nodes defined';
