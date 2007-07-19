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
#from Timba.Trees import TDL_Joneset
from numarray import *
from copy import deepcopy
import os
#from Timba.Contrib.AGW.clar_source_model import *
from clar_source_model import *

# MS name
msname = "TEST_CLAR_27-480.MS";
tile_size = 480
resample = None;
# resample = [480,1];
num_stations = 27

# MEP table for derived quantities fitted in this script
mep_derived = 'CLAR_DQ_27-480.mep';

# bookmark
Settings.forest_state = record(bookmarks=[
  record(name='Derived quantities',page=[
    record(viewer="Result Plotter",udi="/node/exp_v_gain:1:src_2",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/EXP_V_GAIN:1:src_2",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/ce_vgain:1:src_2",pos=(0,2)),
    record(viewer="Result Plotter",udi="/node/exp_v_gain:%d:src_2"%num_stations,pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/EXP_V_GAIN:%d:src_2"%num_stations,pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/ce_vgain:%d:src_2"%num_stations,pos=(1,2)),
    record(viewer="Result Plotter",udi="/node/uvw:%d"%(num_stations/2),pos=(2,0)),
    record(viewer="Result Plotter",udi="/node/UVW:%d"%(num_stations/2),pos=(2,1)),
    record(viewer="Result Plotter",udi="/node/ce_uvw:%d"%(num_stations/2),pos=(2,2)),
    record(viewer="Result Plotter",udi="/node/solver_uvw:10",pos=(3,0)),
    record(viewer="Result Plotter",udi="/node/solver_vgain:1",pos=(3,1)),
    record(viewer="Result Plotter",udi="/node/solver_vgain:%d"%num_stations,pos=(3,2)),
#    record(viewer="Result Plotter",udi="/node/predict:1:6",pos=(3,1)),
#    record(viewer="Result Plotter",udi="/node/predict:1:14",pos=(3,2)),
#   record(viewer="Result Plotter",udi="/node/stokes:Q:3C343",pos=(1,0)),
#    record(viewer="Result Plotter",udi="/node/stokes:Q:3C343_1",pos=(1,1)),
#   record(viewer="Result Plotter",udi="/node/solver",pos=(1,1)),
  ]) \
]);


# define defaults for station locations, field centre etc
def forest_measurement_set_info(ns, num_ant):
    ns.ra0    << Meq.Constant(0.0)
    ns.dec0   << Meq.Constant(0.0)
    ns.radec0 << Meq.Composer(ns.ra0, ns.dec0)


    for i in range(num_ant):
        station= str(i+1)

        ns.x(station) << Meq.Constant(0.0)
        ns.y(station) << Meq.Constant(0.0)
        ns.z(station) << Meq.Constant(0.0)
        if i == 0:
            ns.xyz0 << Meq.Composer(ns.x(1), ns.y(1),ns.z(1))
            pass

        ns.xyz(station)  << Meq.Composer(ns.x(station),
                                         ns.y(station),
                                         ns.z(station))
        ns.uvw(station) << Meq.UVW(radec= ns.radec0,
                                   xyz_0= ns.xyz0,
                                   xyz  = ns.xyz(station))
        pass
    pass

def create_polc_ft(degree_f=0, degree_t=0, c00=0.0):
    polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0)
    polc.coeff[0,0] = c00
    return polc

# creates common nodes (field centre):
def create_common_nodes(ns):
    """ set up various nodes with default or constant values """
# field centre: these two values will be over-written later with
# values obtained from the input MS
    ns.ra0 << Meq.Constant(0.0)
    ns.dec0 << Meq.Constant(0.0)

def create_constant_nodes(ns):
# numeric constants
    ns.one << Meq.Constant(1.0)
    ns.half << Meq.Constant(0.5)
    ns.ln_16 << Meq.Constant(-2.7725887)
# create width parameter for CLAR beam nodes
# base HPW is 647.868 1/rad at 800 Mhz
    ns.width << Meq.Constant(647.868);
    # this scales it with frequency
    ns.width_fq << ns.width * ( Meq.Freq() / float(800*1e+6 ) );
    ns.width_sq << Meq.Sqr(ns.width_fq)

# creates source-related nodes for a given source
def forest_source_subtrees (ns, source):
  print 'source.name ', source.name
  ra = ns.ra(source.name) << Meq.Parm(source.ra, table_name=source.table,
			node_groups='Parm')
  dec= ns.dec(source.name) << Meq.Parm(source.dec, table_name=source.table,
			node_groups='Parm')
  radec = ns.radec(source.name) << Meq.Composer(ra, dec)
  lmn   = ns.lmn  (source.name) << Meq.LMN(radec_0 = ns.radec0, radec = radec)
  n     = ns.n    (source.name) << Meq.Selector(lmn, index=2)

  pass


def create_station_subtrees(ns,st):
  # create nodes used to calculate AzEl of field centre as seen
  # from a specific station

  # first create AzEl node for field_centre as seen from this station
  ns.AzEl_fc(st) << Meq.AzEl(radec=ns.radec0, xyz=ns.xyz(st))

  # then get elevation of FC as seen from this station as separate element
  ns.AzEl_el0(st) << Meq.Selector(ns.AzEl_fc(st),index=1)

  # get squared sine of elevation of field centre - used later to determine CLAR
  # beam broadening
  ns.sin_el_sq(st) << Meq.Sqr(Meq.Sin(ns.AzEl_el0(st)))


def create_beam_subtrees (ns, st,src):
# builds an init-record for a beam tree for one station qand source
#
# we first build up the mathematical expression of a CLAR voltage
# pattern for a source using the equations
# log16 =  (-1.0) * log(16.0)
# L,M give direction cosines of the source wrt field centre in
# AzEl coordinate frame
# L_gain = (L * L) / (widthl_ * widthl_)
# sin_factor = sqr(sin(field centre elevation))
# M_gain = (sin_factor * M * M ) / (widthm_ * widthm_)
# voltage_gain = sqrt(exp(log16 * (L_gain + M_gain)))

# see the create_station_subtrees function for creation
# of nodes used to compute Az, El of field centre

  # create AzEl node for source as seen from this station
  ns.az_el(st,src.name) << Meq.AzEl(radec=ns.radec(src.name), xyz=ns.xyz(st))

  # do computation of LMN of source wrt field centre in AzEl frame
  ns.lmn_azel(st,src.name) << Meq.LMN(radec_0=ns.AzEl_fc(st), radec=ns.az_el(st,src.name))
  ns.l_azel(st,src.name) << Meq.Selector(ns.lmn_azel(st,src.name),index=0)
  ns.m_azel(st,src.name) << Meq.Selector(ns.lmn_azel(st,src.name),index=1)
			    
  # compute CLAR voltage gain as seen for this source at this station
  # first square L and M
  ns.l_sq(st,src.name) << Meq.Sqr(ns.l_azel(st,src.name))
  ns.m_sq(st,src.name) << Meq.Sqr(ns.m_azel(st,src.name))

  # then multiply by width squared, for L, M
#  ns.l_vpsq(st,src.name) << ns.l_sq(st,src.name) * ns.width_l_sq
#  ns.m_vpsq(st,src.name) << ns.m_sq(st,src.name) * ns.width_m_sq

  # for M, adjust by sin of elevation squared
#  ns.m_vpsq_sin(st,src.name) << ns.m_vpsq(st,src.name) * ns.sine_el_sq(st)

  # add L and M gains together, then multiply by log 16
  ns.v_gain(st,src.name) << \
      (ns.l_sq(st,src.name) + ns.m_sq(st,src.name)*ns.sin_el_sq(st))*ns.ln_16;
# this now needs to be multiplied by width and exponent taken to get the
# true beam power
  # raise to exponent
  ns.exp_v_gain(st,src.name) << Meq.Exp(ns.v_gain(st,src.name)*ns.width_sq)

  # Note: this final node represents a source seen in a 'power pattern'
  # we take the square root of this value, so as to have a voltage response,
  # when computing Jones matrix responses - see forest_station_source_jones
# ---


def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc_ft(degree_f=0, degree_t=tdeg,c00=c00),
                  node_groups='Parm',
                  table_name=mep_derived);
  

def create_solver_defaults(num_iter=30,epsilon=1e-4,convergence_quota=0.9,solvable=[]):
    solver_defaults=record()
    solver_defaults.num_iter     = num_iter
    solver_defaults.epsilon      = epsilon
    solver_defaults.convergence_quota = convergence_quota
    solver_defaults.save_funklets= True
    solver_defaults.last_update  = True
#See example in TDL/MeqClasses.py
    solver_defaults.solvable     = solvable
    return solver_defaults
    
def forest_solver(ns, station_list, sources):
  solver_list = []
  # Measurements
  for sta in station_list:
    # create solver + condeq for station UVWs
    ns.ce_uvw(sta) << Meq.Condeq(
      ns.uvw(sta),
      ns.UVW(sta) << Meq.Composer(
        ns.U(sta) << tpolc(5),
        ns.V(sta) << tpolc(5),
        ns.W(sta) << tpolc(5) )
    );
    defs = create_solver_defaults(solvable=[node(sta).name for node in (ns.U,ns.V,ns.W)])
    solver_list.append(ns.solver_uvw(sta) << Meq.Solver(
        ns.ce_uvw(sta),mt_polling=False,mt_solve=False,**defs));
    # create solver for station beams patterns
    for src in sources:
      # condeq for source-station E-term
      vgain = ns.V_GAIN(sta,src.name) << tpolc(6);
      ns.ce_vgain(sta,src.name) << Meq.Condeq(
          ns.exp_v_gain(sta,src.name),
          ns.EXP_V_GAIN(sta,src.name) << Meq.Exp(vgain*ns.width_sq)
      );
    condeqs = [ ns.ce_vgain(sta,src.name) for src in sources ];
    defs = create_solver_defaults(solvable=[ns.V_GAIN(sta,src.name).name for src in sources]);
    solver_list.append(ns.solver_vgain(sta) << Meq.Solver(mt_polling=False,mt_solve=False,
        *[ns.ce_vgain(sta,src.name) for src in sources],**defs));
  # create ReqMux for all solvers
  ns.solvers << Meq.ReqMux(mt_polling=True,*solver_list);
  if resample:
    ns.modres << Meq.ModRes(ns.solvers,num_cells=resample);


def forest_create_vdm (ns):
  global _vdm;
  if resample:
    _vdm = ns.VisDataMux << Meq.VisDataMux(pre=ns.modres);
  else:
    _vdm = ns.VisDataMux << Meq.VisDataMux(pre=ns.solvers);


def create_inputrec(msname, tile_size=1500,short=False):
    boioname = "boio."+msname+"."+str(tile_size);
    # if boio dump for this tiling exists, use it to save time
    # but watch out if you change the visibility data set!
    if False: # not short and os.access(boioname,os.R_OK):
      rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
    # else use MS, but tell the event channel to record itself to boio file
    else:
      rec = record();
      rec.ms_name          = msname
      rec.data_column_name = 'DATA'
      rec.tile_size        = tile_size
#      rec.selection = record(channel_start_index=0,
#                             channel_end_index=0,
#                             channel_increment=1,
#                             selection_string='')
#      if short:
#        rec.selection.selection_string = '';
#      else:
#        rec.record_input = boioname;
      rec = record(ms=rec);
    rec.python_init='AGW_read_msvis_header.py';
    return rec;


def create_outputrec(output_column='CORRECTED_DATA'):
    rec=record()

    rec.write_flags=False
    rec.predict_column=output_column

    return record(ms=rec);

def set_AGW_node_state (mqs, node, fields_record):
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


def publish_node_state(mqs, nodename):
    mqs.meq('Node.Set.Publish.Level',record(name=nodename,level=1))
    pass

########### new-style TDL stuff ###############

def _tdl_job_fit_derived_parameters (mqs,parent,write=True):
#   inputrec        = create_inputrec(msname, tile_size=6000)
    inputrec        = create_inputrec(msname, tile_size=tile_size)
    outputrec       = create_outputrec(output_column='PREDICT')
    print 'input record ', inputrec
    print 'output record ', outputrec
    
    req = meq.request();
    req.input  = inputrec;
    if write:
      req.output = outputrec;
    mqs.clearcache('VisDataMux');
    print 'VisDataMux request is ', req
    mqs.execute('VisDataMux',req,wait=(parent is None));
    pass

####################
def _define_forest(ns):

# Note: To create a predictor:just eliminate the ReqSeqs, Spigots, Solver,
# Condeqs and Subtracts, and make each predict node (i.e. the non-spigot
# side of the condeq) a direct child of the corresponding Sink

# define default field centre
  create_common_nodes(ns)

# create constant value nodes for CLAR
  create_constant_nodes(ns)

# create default antenna station parameters (location, UVW)
  station_list = range(1, num_stations+1)
  forest_measurement_set_info(ns, len(station_list))

# create source list
  source_mep_tablename= 'sourcemodel.mep'
  source_model = create_source_model(tablename=source_mep_tablename)

# create nodes specific to individual sources in the source list
  for source in source_model:
      forest_source_subtrees(ns, source)
      pass

  for station in station_list:
# first create nodes used to calculate AzEl of field centre 
# as seen from a specific station
    create_station_subtrees(ns, station)

# First, compute CLAR beam parameters (power pattern) for all 
# stations and source. 
    for source in source_model:
      create_beam_subtrees(ns,station,source);

  forest_solver(ns,station_list,source_model);
  forest_create_vdm(ns);


Settings.forest_state.cache_policy = 1  # 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = False

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
