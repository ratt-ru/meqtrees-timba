# file: ../Grunting/JEN_Meow_Utils.py

# This is a (temporary) copy of ../contrib/OMS/Meow/Utils.py
# It allows me to try (small) modifications based on hard experience,
# that might find their way into the original eventually.
# All modifications are clearly marked, dated and ecplained in the text:
#   JEN_14jan2007: ....


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

from Timba.TDL import *
from Timba.Meq import meq
import numarray
import math
import random
import Meow

input_column = output_column = None;
tile_size = None;
msname = '';



def include_ms_options (has_input=True, has_output=True, tile_sizes=[1,5,10,20,30,60]):
  """Instantiates MS input/output options""";
  ms_list = filter(lambda name:name.endswith('.ms') or name.endswith('.MS'),os.listdir('.'));
  if not ms_list:
    ms_list = [ "no MSs found" ];
  TDLRuntimeOption('msname',"MS",ms_list);
  if has_input:
    input_menu = ["DATA","MODEL_DATA","CORRECTED_DATA"]
    # JEN_15jan2007: Allow specification of the default output col:
    if isinstance(has_input, str):
      input_menu.insert(0,has_input)
    TDLRuntimeOption('input_column', "Input MS column", input_menu, default=0);
  if has_output:
    # JEN_14jan2007: The default (DATA) is dangerous. I prefer CORRECTED_DATA.
    output_menu = ["CORRECTED_DATA","MODEL_DATA","DATA", None]
    # JEN_15jan2007: Allow specification of the default output col:
    if isinstance(has_output, str):
      output_menu.insert(0,has_output)
    TDLRuntimeOption('output_column', "Output MS column", output_menu, default=0);
  if tile_sizes:
    TDLRuntimeOption('tile_size',"Tile size (timeslots)",tile_sizes, more=int);

imaging_npix = 256;
imaging_cellsize = '1arcsec';
imaging_channels = [32,1,1];



def include_imaging_options (npix=None,cellsize=None,channels=None):
  """Instantiates imager options""";
  TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  TDLRuntimeOption('imaging_weight',"Imaging weights",["natural","uniform","briggs"]);
  TDLRuntimeOption('imaging_stokes',"Stokes parameters to image",["I","IQUV"]);
  if npix:
    if not isinstance(npix,(list,tuple)):
      npix = [ npix ];
    TDLRuntimeOption('imaging_npix',"Image size, in pixels",npix);
  if cellsize:
    if not isinstance(cellsize,(list,tuple)):
      cellsize = [ cellsize ];
    TDLRuntimeOption('imaging_cellsize',"Pixel size",cellsize);
  if channels:
    TDLRuntimeOption('imaging_channels',"Imaging channels selection",channels);
  

source_table = "sources.mep";
mep_table = "calib.mep";



def get_source_table ():
  return msname + "/" + source_table;



def get_mep_table ():
  return msname + "/" + mep_table;



def solver_options ():
  """Returns list of solver option""";
  return [
    TDLOption('solver_debug_level',"Solver debug level",[0,1,10]),
    TDLOption('solver_colin_factor',"Collinearity factor",[1e-8,1e-7,1e-6,1e-5,1e-4,1e-3,1e-2,1e-1]),
    TDLOption('solver_lm_factor',"Initial LM factor",[1,.1,.01,.001]),
    TDLOption('solver_balanced_equations',"Assume balanced equations", False),
    TDLOption('solver_epsilon',"Convergence threshold",[.01,.001,.0001,1e-5,1e-6]),
    # JEN: 19jan2007: Extend the menu with fewer than 30, and allow more
    TDLOption('solver_num_iter',"Max iterations",[5,1,2,3,5,10,30,50,100,1000], more=int),
    TDLOption('solver_convergence_quota',"Convergence quota",[.8,.9,1.]) \
  ];



def parameter_options ():
  return [
    TDLOption('use_previous',"Reuse solution from previous time interval",False,
    doc="""If True, solutions for successive time domains will start with
  the solution for a previous domain. Normally this speeds up convergence; you
  may turn it off to re-test convergence at each domain."""),
    TDLOption('use_mep',"Reuse solutions from MEP table",False,
    doc="""If True, solutions from the MEP table (presumably, from a previous
  run) will be used as starting points. Turn this off to solve from scratch.""")
 ];



def create_solver_defaults(solvable=[]):
  solver_defaults = record()
  solver_defaults.num_iter      = solver_num_iter
  solver_defaults.epsilon       = solver_epsilon
  solver_defaults.epsilon_deriv = solver_epsilon
  solver_defaults.lm_factor     = solver_lm_factor
  solver_defaults.convergence_quota = solver_convergence_quota
  solver_defaults.balanced_equations = solver_balanced_equations
  solver_defaults.debug_level   = solver_debug_level;
  solver_defaults.save_funklets = True
  solver_defaults.last_update   = True
  solver_defaults.solvable      = record(command_by_list=(record(name=solvable,
                                       state=record(solvable=True)),
                                       record(state=record(solvable=False))))
  return solver_defaults


#===================================================================================


def set_node_state (mqs,node,fields_record):
  """helper function to set the state of a node specified by name or
  nodeindex""";
  rec = record(state=fields_record);
  if isinstance(node,str):
    rec.name = node;
  elif isinstance(node,int):
    rec.nodeindex = node;
  else:
    raise TypeError,'illegal node argument';
  # pass command to kernel
  mqs.meq('Node.Set.State',rec);
  pass

# various global MS I/O options
ms_output = True;
ms_queue_size = 500;
ms_selection = None;




def create_inputrec (tiling=None):
  global tile_size;
  boioname = "boio."+msname+".predict."+str(tiling or tile_size);
  # if boio dump for this tiling exists, use it to save time
  if not ms_selection and os.access(boioname,os.R_OK):
    rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
  # else use MS, but tell the event channel to record itself to boio file
  else:
    rec = record();
    rec.ms_name          = msname
    if input_column:
      rec.data_column_name = input_column;
    # use global tile_size setting if tiling not specified
    if not tiling:
      tiling = tile_size;
    if isinstance(tiling,(list,tuple)):
      if len(tiling) != 2:
        raise TypeError,"tiling: 2-list or 2-tuple expected";
      (tile_segments,tile_size) = tiling;
      if tile_segments is not None:
        rec.tile_segments    = tile_segments;
      if tile_size is not None:
        rec.tile_size        = tile_size;
    else:  
      rec.tile_size = tiling;
    rec.selection = ms_selection or record();
    rec = record(ms=rec);
  rec.python_init = 'Meow.ReadVisHeader';
  rec.mt_queue_size = ms_queue_size;
  return rec;



def create_outputrec (inhibit_output=False):
  rec = record();
  rec.mt_queue_size = ms_queue_size;
  if ms_output:
    rec.write_flags    = False;
    if output_column:
      rec.data_column = output_column;
    return record(ms=rec);
  else:
    rec.boio_file_name = "boio."+msname+".solve."+str(tile_size);
    rec.boio_file_mode = 'W';
    return record(boio=rec);
    

# JEN_14jan2007: Added override_output_column option, for safety
# (e.g. Grunting/inspectMS.py)

def create_io_request (tiling=None, override_output_column=False):
  req = meq.request();
  req.input  = create_inputrec(tiling);
  global output_column                                  # JEN_17jan2007 (see above)
  if not isinstance(override_output_column, bool):      # JEN_14jan2007 (see above)
    output_column = override_output_column         
  if output_column is not None:
    req.output = create_outputrec();
  return req;
  

#===================================================================================


def phase_parm (tdeg,fdeg):
  """helper function to create a t/f parm for phase, including constraints.
  Placeholder until Maaijke implements periodic constraints.
  """;
  polc = meq.polc(numarray.zeros((tdeg+1,fdeg+1))*0.0,
            scale=array([3600.,8e+8,0,0,0,0,0,0]));
  shape = [tdeg+1,fdeg+1];
  # work out constraints on coefficients
  # maximum excursion in freq is pi/2
  # max excursion in time is pi/2
  dt = .2;
  df = .5;
  cmin = [];
  cmax = [];
  for it in range(tdeg+1):
    for jf in range(fdeg+1):
      mm = math.pi/(dt**it * df**jf );
      cmin.append(-mm);
      cmax.append(mm);
  cmin[0] = -1e+9;
  cmax[0] = 1e+9;
  return Meq.Parm(polc,shape=shape,real_polc=polc,node_groups='Parm',
                  constrain_min=cmin,constrain_max=cmax,
                  table_name=get_mep_table());




def perturb_parameters (mqs,solvables,pert="random",
                        absolute=False,random_range=[0.2,0.3],constrain=None):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if absolute:  # absolute pert value given
      polc.coeff[0,0] += pert;
    elif pert == "random":  # else random pert
      polc.coeff[0,0] *= 1 + random.uniform(*random_range)*random.choice([-1,1]);
    else: # else perturb in relative terms
      polc.coeff[0,0] *= (1 + pert);
    parmstate = record(init_funklet=polc,
      use_previous=use_previous,reset_funklet=not use_mep);
    if constrain is not None:
      parmstate.constrain = constrain;
    set_node_state(mqs,name,parmstate);
  return solvables;
    


def reset_parameters (mqs,solvables,value=None,use_table=False,reset=False):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if value is not None:
      polc.coeff[()] = value;
    reset_funklet = reset or not (use_table or use_mep);
    set_node_state(mqs,name,record(init_funklet=polc,
      use_previous=use_previous,reset_funklet=reset_funklet));
  return solvables;



def run_solve_job (mqs,solvables,tiling=None,solver_node="solver",vdm_node="VisDataMux"):
  """common helper method to run a solution with a bunch of solvables""";
  # set solvables list in solver
  solver_defaults = create_solver_defaults(solvable=solvables)
  set_node_state(mqs,solver_node,solver_defaults)

  req = create_io_request(tiling);
  
  mqs.execute(vdm_node,req,wait=False);
  pass
  

#===================================================================================

def make_dirty_image (npix=None,cellsize=None,arcmin=None,channels=None):
  """Runs glish script to make an image
  npix is image size, in pixels
  cellsize is pixel size, as an aips++ Measures string (e.g. "0.5arcsec")
  arcmin is image size, in arcminutes. Either cellsize or arcmin must be 
        specified, but not both.
  """;
  if not output_column:
    raise ValueError,"make_dirty_image: output column not set up";
  if not msname:
    raise ValueError,"make_dirty_image: MS not set up";
  npix = (npix or imaging_npix);
  if arcmin is not None:
    if cellsize is not None:
      raise ValueError,"make_dirty_image: can't specify both 'cellsize' and 'arcmin'";
    cellsize = str(float(arcmin*60)/npix)+"arcsec";
  import os
  import os.path
  (nchan,chanstart,chanstep) = (channels or imaging_channels);
  script_name = os.path.join(Meow._meow_path,'make_dirty_image.g');
  script_name = os.path.realpath(script_name);  # glish don't like symlinks...
  args = [ 'glish','-l',
    script_name,
    output_column,
    'ms='+msname,'mode='+imaging_mode,
    'weight='+imaging_weight,'stokes='+imaging_stokes,
    'npix='+str(npix),
    'cellsize='+(cellsize or imaging_cellsize),
    'nchan='+str(nchan),
    'chanstart='+str(chanstart),    
    'chanstep='+str(chanstep)
  ];
  print args;
  os.spawnvp(os.P_NOWAIT,'glish',args);
  

