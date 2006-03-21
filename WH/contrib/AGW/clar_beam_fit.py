from Timba.TDL import *
from Timba.Meq import meq
from Timba.Trees import TDL_Joneset
from numarray import *
from copy import deepcopy
import os

# MS name
msname = "TEST_CLAR_28-480.MS";
tile_size = 100
resample = None;
# resample = [480,1];


# MEP table for derived quantities fitted in this script
mep_derived = 'CLAR_DQ_28-480.mep';



# bookmark
Settings.forest_state = record(bookmarks=[
  record(name='Derived quantities',page=[
    record(viewer="Result Plotter",udi="/node/exp_v_gain:1:src_2",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/EXP_V_GAIN:1:src_2",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/ce_vgain:1:src_2",pos=(0,2)),
    record(viewer="Result Plotter",udi="/node/exp_v_gain:5:src_2",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/EXP_V_GAIN:5:src_2",pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/ce_vgain:5:src_2",pos=(1,2)),
    record(viewer="Result Plotter",udi="/node/uvw:10",pos=(2,0)),
    record(viewer="Result Plotter",udi="/node/UVW:10",pos=(2,1)),
    record(viewer="Result Plotter",udi="/node/ce_uvw:10",pos=(2,2)),
    record(viewer="Result Plotter",udi="/node/solver1",pos=(3,0)),
    record(viewer="Result Plotter",udi="/node/solver2",pos=(3,1)),
#    record(viewer="Result Plotter",udi="/node/predict:1:6",pos=(3,1)),
#    record(viewer="Result Plotter",udi="/node/predict:1:14",pos=(3,2)),
#   record(viewer="Result Plotter",udi="/node/stokes:Q:3C343",pos=(1,0)),
#    record(viewer="Result Plotter",udi="/node/stokes:Q:3C343_1",pos=(1,1)),
#   record(viewer="Result Plotter",udi="/node/solver",pos=(1,1)),
  ]) \
]);


class PointSource:
    name = ''
    ra   = 0.0
    dec  = 0.0
    IQUV      = zeros(4)*0.0
    IQUVorder = zeros(4)*0.0
    table  = ''

    def __init__(self, name='', ra=0.0, dec=0.0,
                 I=0.0, Q=0.0, U=0.0, V=0.0,
                 Iorder=0, Qorder=0, Uorder=0, Vorder=0,
                 table=''):
        self.name   = name
        self.ra     = ra
        self.dec    = dec
        self.IQUV   = array([I,Q,U,V])
        self.IQUVorder = array([Iorder,Qorder,Uorder,Vorder])
        self.table  = table
        pass
    pass

def create_source_model(tablename=''):
    """ define model source positions and flux densities """
    source_model = []
    source_model.append( PointSource(name="src_1",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.030272885, dec=0.575762621,
                    table=tablename))

    source_model.append( PointSource(name="src_2",  I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0306782675, dec=0.575526087,
                    table=tablename))

    source_model.append( PointSource(name="src_3",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0308948646, dec=0.5762655,
                    table=tablename))

    source_model.append( PointSource(name="src_4",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0308043705, dec=0.576256621,
                    table=tablename))

    source_model.append( PointSource(name="src_5",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.030120036, dec=0.576310965,
                    table=tablename))

    source_model.append( PointSource(name="src_6",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0301734016, dec=0.576108805,
                    table=tablename))

    source_model.append( PointSource(name="src_7",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0302269161, dec=0.576333355,
                    table=tablename))

    source_model.append( PointSource(name="src_8",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0304215356, dec=0.575777607,
                    table=tablename))

    source_model.append( PointSource(name="src_9",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0307416105, dec=0.576347166,
                    table=tablename))

    source_model.append( PointSource(name="src_10",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0306878027, dec=0.575851951,
                    table=tablename))

    return source_model

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
  

def forest_solver(ns, station_list, sources):
  ce_list1 = []
  ce_list2 = []
  # Measurements
  for sta in station_list:
    # condeqs for station UVWs
    ce_list2.append(
      ns.ce_uvw(sta) << Meq.Condeq(
        ns.uvw(sta),
        ns.UVW(sta) << Meq.Composer(
          ns.U(sta) << tpolc(6),
          ns.V(sta) << tpolc(6),
          ns.W(sta) << tpolc(6) )
      ));
    for src in sources:
      # condeq for source-station E-term
      vgain = ns.V_GAIN(sta,src.name) << tpolc(5);
      ce_list1.append(
        ns.ce_vgain(sta,src.name) << Meq.Condeq(
          ns.exp_v_gain(sta,src.name),
          ns.EXP_V_GAIN(sta,src.name) << Meq.Exp(vgain*ns.width_sq)
      ));
  ns.solver1 << Meq.Solver(children=ce_list1);
  ns.solver2 << Meq.Solver(children=ce_list2);
  ns.solvers << Meq.ReqMux(ns.solver1,ns.solver2);
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
      rec.selection = record(channel_start_index=0,
                             channel_end_index=0,
                             channel_increment=1,
                             selection_string='')
      if short:
        rec.selection.selection_string = '';
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

def create_solver_defaults(num_iter=30,epsilon=1e-4,convergence_quota=0.9,solvable=[]):
    solver_defaults=record()
    solver_defaults.num_iter     = num_iter
    solver_defaults.epsilon      = epsilon
    solver_defaults.convergence_quota = convergence_quota
    solver_defaults.save_funklets= True
    solver_defaults.last_update  = True
#See example in TDL/MeqClasses.py
    solver_defaults.solvable     = record(command_by_list=(record(name=solvable,
                                         state=record(solvable=True)),
                                         record(state=record(solvable=False))))
    return solver_defaults

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
    station_list = range(1,15)
#get source list
    source_model = create_source_model()

    solvables1 = []
    solvables2 = []
    for station in station_list:
      solvables2 += [ ':'.join(('U',str(station))),
                     ':'.join(('V',str(station))),
                     ':'.join(('W',str(station))) ];
      for source in source_model:
        solvables1 += [ ':'.join(('V_GAIN',str(station),source.name)) ];

    publish_node_state(mqs, 'solver1')
    publish_node_state(mqs, 'solver2')

    solver_defaults1 = create_solver_defaults(solvable=solvables1)
    set_AGW_node_state(mqs, 'solver1', solver_defaults1)
    solver_defaults2 = create_solver_defaults(solvable=solvables2)
    set_AGW_node_state(mqs, 'solver2', solver_defaults2)

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
  num_antennas = 28
  station_list = range(1, num_antennas+1)
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
              
