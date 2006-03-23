from Timba.TDL import *
from Timba.Meq import meq
from Timba.Trees import TDL_Joneset
from numarray import *
from copy import deepcopy
import os

# MS name
msname = "TEST_CLAR_27-4800.MS";
# number of timeslots to use at once
tile_size = 60

# MS input queue size -- must be at least equal to the no. of ifrs
input_queue_size = 500

num_stations = 27

ms_selection = None
#or record(channel_start_index=0,
#          channel_end_index=0,
#          channel_increment=1,
#          selection_string='')

ms_output = False   # if True, outputs to MS, else to BOIO dump

# CLAR beam width
# base HPW is 647.868 1/rad at 800 Mhz
beam_width = 647.868
ref_frequency = float(800*1e+6)

# MEP table for derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicts',page=[
    record(viewer="Result Plotter",udi="/node/clean_visibility:1:2:src_1",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/clean_visibility:1:2:src_2",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/clean_visibility:1:2:src_5",pos=(0,2)),
    record(viewer="Result Plotter",udi="/node/corrupted_vis:1:2:src_1",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/corrupted_vis:1:2:src_2",pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/corrupted_vis:1:2:src_5",pos=(1,2)),
    record(viewer="Result Plotter",udi="/node/E:1:src_1",pos=(2,0)),
    record(viewer="Result Plotter",udi="/node/E:1:src_5",pos=(2,1)),
    record(viewer="Result Plotter",udi="/node/E:%d:src_5"%num_stations,pos=(2,2)),
    record(viewer="Result Plotter",udi="/node/predict:1:2",pos=(3,0)),
    record(viewer="Result Plotter",udi="/node/predict:1:6",pos=(3,1)),
    record(viewer="Result Plotter",udi="/node/predict:1:%d"%num_stations,pos=(3,2)),
#   record(viewer="Result Plotter",udi="/node/stokes:Q:3C343",pos=(1,0)),
#    record(viewer="Result Plotter",udi="/node/stokes:Q:3C343_1",pos=(1,1)),
#   record(viewer="Result Plotter",udi="/node/solver",pos=(1,1)),
  ]),
  record(name='Source fluxes',page=[
    record(viewer="Result Plotter",udi="/node/stokes:I:src_1",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_2",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_3",pos=(0,2)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_4",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_5",pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_6",pos=(1,2)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_7",pos=(2,0)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_8",pos=(2,1)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_9",pos=(2,2)),
    record(viewer="Result Plotter",udi="/node/stokes:I:src_10",pos=(3,0)),
    record(viewer="Result Plotter",udi="/node/width_fq",pos=(3,1)),
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
                 spi=0.0,
                 table=''):
        self.name   = name
        self.ra     = ra
        self.dec    = dec
        self.IQUV   = array([I,Q,U,V])
        self.IQUVorder = array([Iorder,Qorder,Uorder,Vorder])
        self.spi    = spi
        self.table  = table
        pass
    pass

def create_source_model(tablename=''):
    """ define model source positions and flux densities """
    source_model = []
    source_model.append( PointSource(name="src_1",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.030272885, dec=0.575762621,
                    spi=-0.71,
                    table=tablename))

    source_model.append( PointSource(name="src_2",  I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0306782675, dec=0.575526087,
                    spi=-0.62,
                    table=tablename))

    source_model.append( PointSource(name="src_3",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0308948646, dec=0.5762655,
                    spi=-0.53,
                    table=tablename))

    source_model.append( PointSource(name="src_4",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0308043705, dec=0.576256621,
                    spi=-0.44,
                    table=tablename))

    source_model.append( PointSource(name="src_5",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.030120036, dec=0.576310965,
                    spi=-0.35,
                    table=tablename))

    source_model.append( PointSource(name="src_6",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0301734016, dec=0.576108805,
                    spi=-0.26,
                    table=tablename))

    source_model.append( PointSource(name="src_7",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0302269161, dec=0.576333355,
                    spi=-0.17,
                    table=tablename))

    source_model.append( PointSource(name="src_8",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0304215356, dec=0.575777607,
                    spi=-0.28,
                    table=tablename))

    source_model.append( PointSource(name="src_9",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0307416105, dec=0.576347166,
                    spi=-0.39,
                    table=tablename))

    source_model.append( PointSource(name="src_10",I=1.0, Q=0.0, U=0.0, V=0.0,
                    Iorder=0, ra=0.0306878027, dec=0.575851951,
                    spi=-0.40,
                    table=tablename))

    return source_model

def create_refparms (refnode):
  """For any given parm node, this creates:
  * a reference parms with the same name, linked to a "reference" MEP table called "mep-ref/<meptable>".
  * a Subtract node taking the difference between the two.
  The subtract node is made a child of a root node called "verifier".
  The idea is that it is then easy to execute the verifier node with a request
  corresponding to the entire MS (or a part thereof), and obtain comparisons
  for all parameters between the new solution, and an older solution saved
  in mep-ref/.
  """;
 # ### temp kludge!!!
 # for q in refnode.quals:
 # if isinstance(q,int) and q>3:
 #    return;
  nodename = refnode.name;
  mepname = refnode.initrec().table_name;
  r0 = refnode('ref') << Meq.Parm(0,table_name="mep-ref/"+mepname,node_groups='Ref',parm_name=nodename,cache_policy=100);
  d  = refnode('diff') << Meq.Subtract(r0,refnode,cache_policy=100);
  # create verifier node if not already created
  global _verifier;  # holding global ref to it ensures that it is not cleaned up as an orpan node
  _verifier = refnode.scope.verifier;
  if not _verifier.initialized():
    _verifier << Meq.VisDataMux(pre=\
      refnode.scope.vdc << Meq.DataCollect(cache_policy=100));
  # add to its children
  refnode.scope.vdc.add_children(d);


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
        ns.uvw(station) << Meq.Composer(
          ns.U(station) << Meq.Parm(table_name=mep_derived),
          ns.V(station) << Meq.Parm(table_name=mep_derived),
          ns.W(station) << Meq.Parm(table_name=mep_derived)
        );
        pass
    pass

def create_polc_ft(degree_f=0, degree_t=0, c00=0.0):
    polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0)
    polc.coeff[0,0] = c00
    return polc

def forest_baseline_predict_trees(ns, interferometer_list, sources):
    """ create visibility for a source as seen by station combinations
        with original theoretical visibilities corrupted by Jones matrices
    """    
    for (ant1, ant2) in interferometer_list:
        corrupted_vis_list = []
        for source in sources:
            ns.corrupted_vis(ant1,ant2,source.name) << \
                    Meq.MatrixMultiply(ns.E(ant1,source.name),
                                 ns.clean_visibility(ant1,ant2, source.name),
                                 ns.ctE(ant2, source.name))
            corrupted_vis_list.append(ns.corrupted_vis(ant1,ant2,source.name))
            pass
        # add a noise term
        corrupted_vis_list.append(ns.noise(ant1,ant2) << noise_matrix());
        ns.predict(ant1, ant2) << Meq.Add(*corrupted_vis_list);
        pass
    pass

def forest_clean_predict_trees(ns, source, station_list):
    """ create visibility for a source as seen by station combinations
        without any corruption 
    """    
    for station in station_list:
# compute station-based component of phase shift for this source and station
      ns.dft(station, source.name) << Meq.VisPhaseShift(
                                     lmn=ns.lmn_minus1(source.name),
                                     uvw=ns.uvw(station))
      ns.conjdft(station, source.name) << Meq.Conj(ns.dft(station, source.name))
      pass # for station
    
# Now for this source create baseline-based source visibilities that
# are not corrupted  
    for ant1 in range(len(station_list)):
        for ant2 in range(ant1+1, len(station_list)):
            ns.clean_visibility(station_list[ant1], station_list[ant2], source.name) << \
            Meq.MatrixMultiply(ns.dft(station_list[ant1], source.name),
                                  ns.conjdft(station_list[ant2], source.name),
                                  ns.coherency(source.name))
        pass # for ant2
    pass     # for ant1


def forest_station_source_jones(ns, station_list, source_name):
    """
    create E-Jones (primary beam effects) matrices: station_list is 1-based 
    """
    
    for station in station_list:
      vgain = ns.V_GAIN(station, source_name) << Meq.Parm(table_name=mep_derived);
      ediag = ns.ediag(station,source_name) << Meq.Sqrt(Meq.Exp(vgain*ns.width_sq));
      # create a phase error term
      phase_noise = Meq.GaussNoise(stddev=0.1);
      # note that a scalar is equivalent to a diagonal matrix
      ns.E(station,source_name) << Meq.Matrix22(
            Meq.Polar(ediag,phase_noise),0,0,Meq.Polar(ediag,phase_noise));
      ns.ctE(station, source_name) << Meq.Conj(ns.E(station,source_name))

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
    ns.freq << Meq.Freq;
    # f1/f0 is used for beam widths and spectral indices
    ns.freq_ratio << ns.freq / ref_frequency;

    # beam width at reference frequency
    ns.width << Meq.Constant(beam_width);
    # this scales it with frequency
    ns.width_fq << ns.width * ( ns.freq / ref_frequency );
    ns.width_sq << Meq.Sqr(ns.width_fq)
    
def noise_matrix (stddev=0.1):
  noise = Meq.GaussNoise(stddev=stddev);
# create a 2x2 complex noise matrix
  return Meq.Matrix22(
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise),
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise)
  );
  pass;

# creates source-related nodes for a given source
def forest_source_subtrees (ns, source):
  print 'source.name ', source.name
  IQUVpolcs =[None]*4
  STOKES=["I0","Q","U","V"]
  for (i,stokes) in enumerate(STOKES):
    if(source.IQUV[i] != None):
      print 'i source.IQUV[i] source.IQUVorder ', i, ' ', source.IQUV[i], ' ', source.IQUVorder[i]
      IQUVpolcs[i] = create_polc_ft(degree_f=source.IQUVorder[i], 
					c00= source.IQUV[i])
      pass
    st = ns.stokes(stokes,source.name) << Meq.Parm(IQUVpolcs[i],
					table_name=source.table,
					node_groups='Parm')
#   create_refparms(st);
    pass
  ns.spi(source.name) << Meq.Parm(create_polc_ft(c00=source.spi),
                               	  table_name=source.table,
				  node_groups='Parm');
                                  
  ns.stokes("I",source.name) << \
      ns.stokes("I0",source.name) * Meq.Pow(ns.freq_ratio,ns.spi(source.name));
  
  ns.xx(source.name) << (ns.stokes("I",source.name)+ns.stokes("Q",source.name))*0.5
  ns.yx(source.name) << Meq.ToComplex(ns.stokes("U",source.name),ns.stokes("V",source.name))*0.5
  ns.xy(source.name) << Meq.Conj(ns.yx(source.name))
  ns.yy(source.name) << (ns.stokes("I",source.name)-ns.stokes("Q",source.name))*0.5

  ra = ns.ra(source.name) << Meq.Parm(source.ra, table_name=source.table,
			node_groups='Parm')
  dec= ns.dec(source.name) << Meq.Parm(source.dec, table_name=source.table,
			node_groups='Parm')
  radec = ns.radec(source.name) << Meq.Composer(ra, dec)
  lmn   = ns.lmn  (source.name) << Meq.LMN(radec_0 = ns.radec0, radec = radec)
  n     = ns.n    (source.name) << Meq.Selector(lmn, index=2)

  ns.coherency(source.name) << Meq.Matrix22(ns.xx(source.name),
                                          ns.xy(source.name),
                                          ns.yx(source.name),
                                          ns.yy(source.name));
  
  ns.lmn_minus1(source.name) << Meq.Paster(lmn, n-1, index=2)
  pass



def forest_create_sink_sequence(ns,station_list,interferometer_list, output_column='DATA'):
    for (ant1, ant2) in interferometer_list:
        ns.sink(ant1,ant2) << Meq.Sink(station_1_index=ant1-1,
                                       station_2_index=ant2-1,
                                       flag_bit=4,
                                       corr_index=[0,1,2,3],
                                       flag_mask=-1,
                                       output_col=output_column,
                                       children= ns.predict(ant1, ant2)
                                       )
        pass
    pass
    # set a good child poll order for optimal parallelization
    cpo = [];
    for i in range(len(station_list)/2):
      (ant1,ant2) = station_list[i*2:(i+1)*2];
      cpo.append(ns.sink(ant1,ant2).name);
    # create data mux
    ns.VisDataMux << Meq.VisDataMux(child_poll_order=cpo);
    ns.VisDataMux.add_children(*[ns.sink(ant1,ant2) for (ant1, ant2) in interferometer_list]);


def create_inputrec():
    boioname = "boio."+msname+".empty."+str(tile_size);
    # if boio dump for this tiling exists, use it to save time
    # but watch out if you change the visibility data set!
    if os.access(boioname,os.R_OK):
      rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
    # else use MS, but tell the event channel to record itself to boio file
    else:
      rec = record();
      rec.ms_name          = msname
      rec.data_column_name = 'DATA'
      rec.tile_size        = tile_size
      rec.selection        = ms_selection or record();
      rec.record_input     = boioname;
      rec = record(ms=rec);
    rec.python_init = 'AGW_read_msvis_header.py';
    rec.mt_queue_size = input_queue_size;
    return rec;


def create_outputrec(output_column='DATA'):
    rec=record()
    if ms_output:
      rec.write_flags=False
      rec.data_column=output_column
      return record(ms=rec);
    else:
      rec.boio_file_name = "boio."+msname+".predict."+str(tile_size);
      rec.boio_file_mode = 'W';
      return record(boio=rec);


def publish_node_state(mqs, nodename):
    mqs.meq('Node.Set.Publish.Level',record(name=nodename,level=1))
    pass

########### new-style TDL stuff ###############

def _tdl_job_clar_predict(mqs,parent,write=True):
    inputrec        = create_inputrec()
    outputrec       = create_outputrec(output_column='DATA')
    req = meq.request();
    req.input  = inputrec;
    if write:
      req.output = outputrec;
    # mqs.clearcache('VisDataMux');
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
    station_list = range(1,num_stations+1)
    forest_measurement_set_info(ns, len(station_list))

# create source list
    source_mep_tablename= 'sourcemodel.mep'
    source_model = create_source_model(tablename=source_mep_tablename)

# create nodes specific to individual sources in the source list
    for source in source_model:
        forest_source_subtrees(ns, source)
        pass
        
    for source in source_model:
# First, compute CLAR beam parameters (power pattern) for all 
# stations and source. 
# Then compute uncorrupted visibilities for the source as seen by each
# baseline pair
      forest_clean_predict_trees(ns, source, station_list)

# Now compute Jones matrix components for this source and all stations
      forest_station_source_jones(ns, station_list, source.name)
      pass

# Now using Jones Matrices, compute corrupted visibilities for sources 
# and baselines. Essentially we are predicting that the observed
# visibilities should look like those computed in this step.
    interferometer_list = [(ant1, ant2) for ant1 in station_list for ant2 in station_list if ant1 < ant2]
    forest_baseline_predict_trees(ns, interferometer_list, source_model)

# create sinks to drive system
    forest_create_sink_sequence(ns,station_list,interferometer_list)
    pass


Settings.forest_state.cache_policy = 1  # 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = False

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
