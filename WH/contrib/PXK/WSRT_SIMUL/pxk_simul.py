# Author : Paul Kemper (PXK)
#
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
# - 2006.11.08: added QJones to pxk_jones.py: for test purposes only!
#               added DJones to pxk_jones.py
# - 2006.11.17: separated uv-plane from image-plane effects in JM
# - 2006.11.27: moved creation of truesky to define forest





# standard preamble
from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow
import random
import pxk_manual
import pxk_sourcelist
import pxk_tools
from   pxk_jones import *
import pxk_zjones




# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,60,120,240,720]) 
Meow.Utils.include_imaging_options() 
TDLCompileOption('arcmin',    "FOV (arcmin)",[1,2,5,10,30,60,90,120],default=3)
TDLCompileOption('antennas',  "antennas    ",[14, 27], default=0) 
TDLCompileOption('data_input',"input       ", ['model', 'data']),
TDLCompileOption('residual',  "residual    ",[False, True])
TDLCompileMenu("",
               TDLOption('',"",['a', 'b']),
               TDLOption('',"",['c', 'd']))

ANTENNAS   = range(1,antennas+1)




########################################################################
def _define_forest (ns):
  print "\n____________________________________________________________"

  array       = Meow.IfrArray(ns,ANTENNAS)  # create Array object
  observation = Meow.Observation(ns)        # create Observation object
  patch       = Meow.Patch(ns,'predict', observation.phase_centre) 
  model       = Meow.Patch(ns,'truesky', observation.phase_centre)
  
  # create source list
  slist       = pxk_sourcelist.SourceList(ns, LM=[(1E-100,0)], Q=0.2)
  s_all       = slist.copy()

  # apply source-DE-pendent image-plane effects
  J = ["Z", "M"]
  if "E" in J:
    slist = EJones(ns,slist)
    s_all = EJones(ns,s_all, residual=1)
    pass
  if "F" in J: slist = FJones(ns,slist,array, observation)
  if "Z" in J: slist = pxk_zjones.ZJones(ns,slist,array, observation)
  if "T" in J: pass
  patch.add (*slist.sources)
  model.add (*s_all.sources)
  
  # apply source-IN-dependent uv-plane effects
  if "P" in J: patch = PJones(ns,patch,array, observation)
  if "B" in J: patch = BJones(ns,patch,array)
  if "D" in J: patch = DJones(ns,patch,array)
  if "G" in J: patch = GJones(ns,patch,array)
  if "R" in J: patch = RJones(ns,patch,array, "3.7")
  if "M" in J:
    patch = MJones(ns,patch,array)
    model = MJones(ns,model,array, residual=1)
    pass
  
  # create set of nodes to compute visibilities
  predict = patch.visibilities(array,observation) 
  truesky = model.visibilities(array,observation)
  
  write_data(ns, array, observation, predict, truesky)
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


def write_data (ns, array, observation, predict, model=None):
  """ Create nodes for writing the data. If residual==1, then model
  must also be supplied.
  """
  if residual:
    print "___ Creating residuals nodes"
    output      = ns.residual
    for p,q in array.ifrs(): output(p,q) << predict(p,q) - model(p,q)
    pass
  else:
    print "___ Creatting corrupted nodes"
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
