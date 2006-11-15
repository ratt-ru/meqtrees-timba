# History:
# - 2006.10.23: creation
# - 2006.10.24: added EJones - wsrt beam cos^3(pi/2 rD/lambda)
# - 2006.10.25: made beam strached for X- and Y-feed direction
# - 2006.10.26: added transient in time and frequency
# - 2006.10.27: added moving source -- isn't working yet with Meow
#               since Meow.LMDirection(ns,name,l,m) expects numeric
#               values for 'l' and 'm'
# - 2006.10.30: added job that creates image and opens imager (not
#               working yet
# - 2006.10.31: created pxk_tools.py
#               created pxk_manual.py  -- to simulate without Meow
#               manually added moving source to pxk_manual.py
#               added PJones
# - 2006.11.01: added possibility to write residuals
#               added possibility to read in MS
# - 2006.11.02: added possibility to write residuals WITH beam applied
#               to model, uncorrupted sources
# - 2006.11.06: splitted pxk_sourcelist.py from this file
# - 2006.11.07: moved all Jones matrices to pxk_jones.py
#               added RJones: Errors In Maps
# - 2006.11.08: added QJonesto pxk_jones.py: for test purposes only!




# standard preamble
from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow
import random
import pxk_manual
import pxk_sourcelist
import pxk_tools
import pxk_jones



# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,60,120,240,720]) 
Meow.Utils.include_imaging_options() 
TDLCompileOption('arcmin',    "FOV (arcmin)",[1,5,10,30,60,90,120],default=3)
TDLCompileOption('antennas',  "antennas    ",[14, 27], default=0) 
TDLCompileOption('data_input',"input       ", ['model', 'data']),
TDLCompileOption('residual',  "residual    ",[False, True])
TDLCompileMenu("",
               TDLOption('',"",['a', 'b']),
               TDLOption('',"",['c', 'd']))

ANTENNAS   = range(1,antennas+1)




########################################################################
"""
(!) why is PJones not always 1 for WSRT measurement? Should I simply
    not apply it then?
"""

def _define_forest (ns):
  print "\n____________________________________________________________"
  #pxk_manual.KGE(ns, ANTENNAS)

  array       = Meow.IfrArray(ns,ANTENNAS)  # create Array object
  observation = Meow.Observation(ns)        # create Observation object

  # Make Patches
  patch       = Meow.Patch(ns,'corrupt', observation.phase_centre) 
  
  # create source list
  source_list     = pxk_sourcelist.SourceList(
    ns, kind='cross', lm0=(1e-100,0), nsrc=0)
  source_list_all = pxk_sourcelist.SourceList(LIST = source_list)
  
  # patch with Jones matrices # Jones = ["E", "P", "D", "G", "R"]
  Jones = ["R"]
  if "E" not in Jones: patch.add(*source_list.sources)
  for J in Jones:
    if J=="E": patch = pxk_jones.EJones(ns,patch,source_list)
    if J=="P": patch = pxk_jones.PJones(ns,patch,array, observation)
    if J=="D": patch = pxk_jones.DJones(ns,patch,array)
    if J=="G": patch = pxk_jones.GJones(ns,patch,array, damp=0,dphi=0)
    if J=="R": patch = pxk_jones.RJones(ns,patch,array, "3.6")
    if J=="Q": patch = pxk_jones.QJones(ns,patch,array)
    pass

  
  # create set of nodes to compute visibilities
  predict     = patch.visibilities(array,observation) 
  
  write_data(ns, array, observation, predict, Jones, source_list_all)
  pass




########################################################################
def get_data(ns, array):
  # get source data from MS
  if data_input=='data':
    for p,q in array.ifrs():
      ns.spigot(p,q) << Meq.Spigot(
        input_column='DATA', station_1_index = p-1, station_2_index = q-1)
      pass
    pass
  pass


def write_data (ns, array, observation, predict, Jones=[],
                source_list_all=None):
  """ Write the data. If residual==1, then first the uncorrupted model
  is calculated, for which the beam IS applied first. In that case the
  uncorrupted source_list_all must be supplied.
  """
  
  if residual:
    # create uncorrupted sky model
    uncorrupted = Meow.Patch(ns,'truesky', observation.phase_centre)
    if "E" in Jones:
      uncorrupted = pxk_jones.EJones(
        ns, uncorrupted, source_list_all, residual=1)
      pass
    else: uncorrupted.add(*source_list_all.sources)
    
    print "___ Writing residuals"
    model       = uncorrupted.visibilities(array,observation)
    output      = ns.residual
    for p,q in array.ifrs(): output(p,q) << predict(p,q) - model(p,q)
    pass
  else:
    print "___ Writing corrupted data"
    output = predict
    pass

  # attach visibilities to sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(output(p,q),
                             station_1_index=p-1,
                             station_2_index=q-1, output_col='DATA') 
    pass
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()])
  pass




########################################################################
def _tdl_job_1_simulate_MS (mqs,parent):
  """ Simulate the MS """
  req = Meow.Utils.create_io_request() 
  req.input.python_init = '~/Timba/WH/contrib/PXK/SIM/pxk_visheader.py'
  # execute    
  mqs.execute('vdm',req,wait=False) 
  pass

  
  
def _tdl_job_2_make_image (mqs,parent):
  """ Use the AIPS++ imager to image the MS """
  npix         = 512.0
  FOV          = arcmin*60.0             # Field Of View in arcsec  
  cellsize     = str(FOV/npix)+"arcsec"  # cellsize*npix = FOV
  Meow.Utils.make_dirty_image(npix     = npix,
                              cellsize = cellsize,
                              channels = [32,1,1],
                              msselect="ANTENNA1 != ANTENNA2") 
  pass
  

def _tdl_job_3_open_imager (mqs,parent):
  """ Runs glish script to make an image and view it in imager"""
  # (!) doesn't work yet
  npix          = 512.0
  image_radius  = arcmin*60.0                      # image "radius" in arcsec  
  cellsize      = str(image_radius/npix)+"arcsec"  # cellsize*npix =FOV
  channels      = [32,1,1]
  output_column = 'DATA'
  msname        = 'WSRT.MS'
  imaging_mode  = 'mfs'         # channel
  imaging_weight= "natural"     # "uniform" "briggs"
  imaging_stokes= "I"           # "IQUV"
  
  import os
  import os.path
  (nchan,chanstart,chanstep) = channels
  script_name = 'SCRIPTS/' + 'create_image.g'
  script_name = os.path.realpath(script_name)     # glish don't like symlinks
  args = [ 'glish','-l',
           script_name,
           output_column,
           'ms='+msname,'mode='+imaging_mode,
           'weight='+imaging_weight,'stokes='+imaging_stokes,
           'npix='+str(npix),
           'cellsize='+cellsize,
           'nchan='+str(nchan),
           'chanstart='+str(chanstart),    
           'chanstep='+str(chanstep)
           ] 
  print args 
  os.spawnvp(os.P_NOWAIT,'glish',args) 
  pass



# 'python script.tdl'
if __name__ == '__main__':
  ns = NodeScope() 
  _define_forest(ns) 
  # resolves nodes
  ns.Resolve()   
  print len(ns.AllNodes()),'nodes defined' 
  pass
