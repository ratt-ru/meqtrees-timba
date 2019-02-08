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
from numarray import *
from copy import deepcopy
import os

#from Timba import dmi
#import meqserver

# bookmark
Settings.forest_state = record(bookmarks=[
  record(name='Flux solutions',page=[
    record(viewer="Result Plotter",udi="/node/stokes:I:3C343",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/stokes:I:3C343_1",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/stokes:Q:3C343",pos=(1,0)),
#    record(viewer="Result Plotter",udi="/node/stokes:Q:3C343_1",pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/solver",pos=(1,1)),
  ]), \
  record(name='Phase solutions',page=[
    record(viewer="Result Plotter",udi="/node/JP:2:centre:11",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/JP:2:edge:11",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/solver",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/corrected:2:11",pos=(1,1)) \
  ]),
  record(name='Gain solutions',page=[
    record(viewer="Result Plotter",udi="/node/JA:2:centre:11",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/JA:2:edge:11",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/solver",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/corrected:2:11",pos=(1,1)) \
  ])
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






def create_polc_ft(degree_f=0, degree_t=0, c00=0.0):
    polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0) 
    polc.coeff[0,0] = c00
    return polc


def set_MAB_node_state (mqs, node, fields_record):
    """helper function to set the state of a node specified by name or
    nodeindex""";
    rec = record(state=fields_record);
    if isinstance(node,str):
        rec.name = node;
    elif isinstance(node,int):
        rec.nodeindex = node;
    else:
        raise TypeError('illegal node argumnent');
# pass command to kernel
    mqs.meq('Node.Set.State',rec);
    pass


def publish_node_state(mqs, nodename):
    mqs.meq('Node.Set.Publish.Level',record(name=nodename,level=1))
    pass



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







def create_initial_source_model(tablename='', extra_sources_filename=''):
    source_model = []
    src_3C343_1 = PointSource(name='3C343_1',
                              I=1.0, Q=0.0, U=0.0, V=0.0,
                              Iorder=1, Qorder=1,
                              ra=4.356645791155902,dec=1.092208429052697,
                              table=tablename)
    src_3C343 = PointSource(name='3C343',
                            I=1.0, Q=0.0, U=0.0, V=0.0,
                            Iorder=3, Qorder=3,
                            ra=4.3396003966265599,dec=1.0953677174056471,
                            table=tablename)
    source_model.append(src_3C343_1)
    source_model.append(src_3C343)
    extra_sources=[]
    extra_sources_filename=''
    if extra_sources_filename != '':
        infile = open(extra_sources_filename, 'r')
        lines = infile.readlines()
        infile.close()
        for index,line in enumerate(lines):
            splitup = line.split()
            csplitup = len(splitup)
            if csplitup > 2:
                ra  = float(splitup[0])
                dec = float(splitup[1])
                I   = float(splitup[2])
                pass
            Q = 0.0
            U = 0.0
            V = 0.0
            src = PointSource(name='extra_'+str(index),
                              ra=ra, dec=dec,
                              I=I,Q=Q,U=U,V=V,
                              Iorder=3, Qorder=3, Uorder=3,Vorder=0,
                              table=tablename)
            extra_sources.append(deepcopy(src))
            pass
        pass
    return source_model,extra_sources


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


def forest_source_subtrees(ns, source):
    IQUVpolcs =[None]*4

    STOKES=["I","Q","U","V"]
    
    for (i,stokes) in enumerate(STOKES):
        if(source.IQUV[i] != None):
            IQUVpolcs[i] = create_polc_ft(degree_f=source.IQUVorder[i], 
                                          c00= source.IQUV[i])
            pass
        st = ns.stokes(stokes, source.name) << Meq.Parm(IQUVpolcs[i],
                                                  table_name=source.table,
                                                  node_groups='Parm')
        create_refparms(st);
        pass    

    ns.xx(source.name) << (ns.stokes("I",source.name)+ns.stokes("Q",source.name))*0.5
    ns.yx(source.name) << Meq.ToComplex(ns.stokes("U",source.name),ns.stokes("V",source.name))*0.5
    ns.xy(source.name) << Meq.Conj(ns.yx(source.name))
    ns.yy(source.name) << (ns.stokes("I",source.name)-ns.stokes("Q",source.name))*0.5

    ra    = ns.ra   (source.name) << Meq.Parm(source.ra, table_name=source.table,
                                              node_groups='Parm')
    dec   = ns.dec  (source.name) << Meq.Parm(source.dec, table_name=source.table,
                                              node_groups='Parm')
    radec = ns.radec(source.name) << Meq.Composer(ra, dec)
    lmn   = ns.lmn  (source.name) << Meq.LMN(radec_0 = ns.radec0, radec = radec)
    n     = ns.n    (source.name) << Meq.Selector(lmn, index=2)

    ns.lmn_minus1(source.name) << Meq.Paster(lmn, n-1, index=2)
   
    ns.coherency(source.name) << Meq.Matrix22(ns.xx(source.name),
                                        ns.xy(source.name),
                                        ns.yx(source.name),
                                        ns.yy(source.name))/ns.n(source.name)
    pass








def forest_station_patch_jones(ns, station, patch_name, mep_table_name):
    """
    Station is a 1-based integer. patch_name refers to a collection of sources
    """
    
    for i in range(1,3):
        for j in range(1,3):
            elem      = str(i)+str(j)
            if i != j:
                gain_polc  = create_polc_ft(degree_f=0, degree_t=0, c00=0.0)
                phase_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.0)
            else:
                gain_polc  = create_polc_ft(degree_f=1, degree_t=0, c00=1.0)
                phase_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.0)
                pass
            ja = ns.JA(station, patch_name, elem) << Meq.Parm(gain_polc,
                                                          table_name=mep_table_name,
                                                          node_groups='Parm',
                                                          tiling=record(time=1))
            jp = ns.JP(station, patch_name, elem) << Meq.Parm(phase_polc,
                                                          table_name=mep_table_name,
                                                          node_groups='Parm',
                                                          tiling=record(time=1))
            ns.J(station, patch_name, elem) << Meq.Polar(ja,jp);
            if i == j:
              create_refparms(ja);
              create_refparms(jp);
            pass # for j ...
        pass     # for i ...
    
    ns.J(station,patch_name) << Meq.Matrix22(ns.J(station, patch_name, '11'),
                                             ns.J(station, patch_name, '12'),
                                             ns.J(station, patch_name, '21'),
                                             ns.J(station, patch_name, '22'))
    ns.ctJ(station, patch_name) << Meq.ConjTranspose(ns.J(station,patch_name))
    return ns.J(station, patch_name)













def forest_station_jones(ns, station, mep_table_name):
    """
    Station is a 1-based integer. patch_name refers to a collection of sources
    """
    
    for i in range(1,3):
        for j in range(1,3):
            elem      = str(i)+str(j)
            if i != j:
                gain_polc  = create_polc_ft(degree_f=0, degree_t=0, c00=0.0)
                phase_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.0)
            else:
                gain_polc  = create_polc_ft(degree_f=0, degree_t=1, c00=1.0)
                phase_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.0)
                pass
            ga = ns.GA(station, elem) << Meq.Parm(gain_polc,
                                             table_name=mep_table_name,
                                             node_groups='Parm',
                                             tiling=record(time=20))
            gp = ns.GP(station, elem) << Meq.Parm(phase_polc,
                                             table_name=mep_table_name,
                                             node_groups='Parm',
                                             tiling=record(time=1))
            ns.G(station, elem) << Meq.Polar(ga,gp);
            if i == j:
              create_refparms(ga);
              create_refparms(gp);
            pass # for j ...
        pass     # for i ...
    
    ns.G(station) << Meq.Matrix22(ns.G(station, '11'),
                                  ns.G(station, '12'),
                                  ns.G(station, '21'),
                                  ns.G(station, '22'))
    ns.ctG(station) << Meq.ConjTranspose(ns.G(station))
    return ns.G(station)












def forest_clean_patch_predict_trees(ns, patch_name, source_list, station_list):
    
    # create station-source dfts
    for source in source_list:
        for station in station_list:
            ns.dft(station, source.name) << Meq.VisPhaseShift(
                                                 lmn=ns.lmn_minus1(source.name),
                                                 uvw=ns.uvw(station))
            ns.conjdft(station, source.name) << Meq.Conj(ns.dft(station, source.name))
            pass # for station
        pass #for source
    
    # Create source visibilities per baseline and add to 
    # obtain total visibility due to this patch

    for ant1 in range(len(station_list)):
        for ant2 in range(ant1+1, len(station_list)):
            clean_visibility_list = []
            for source in source_list:
                ns.clean_visibility(station_list[ant1], station_list[ant2], source.name) << \
                     Meq.MatrixMultiply(ns.dft(station_list[ant1], source.name),
                                  ns.conjdft(station_list[ant2], source.name),
                                  ns.coherency(source.name))
                clean_visibility_list.append(ns.clean_visibility(station_list[ant1], station_list[ant2], source.name))
                pass # for source
            ns.clean_visibility(station_list[ant1], station_list[ant2], patch_name) << Meq.Add(children=clean_visibility_list)
            pass # for ant2
        pass     # for ant1
    pass









def forest_baseline_predict_trees(ns, interferometer_list, patch_names):
    for (ant1, ant2) in interferometer_list:
        corrupted_patch_vis_list = []
        for patch_name in patch_names:
            ns.corrupted_patch_vis(ant1,ant2,patch_name) << \
                    Meq.MatrixMultiply(ns.J(ant1,patch_name), 
                                 ns.clean_visibility(ant1,ant2, patch_name),
                                 ns.ctJ(ant2, patch_name))
            corrupted_patch_vis_list.append(ns.corrupted_patch_vis(ant1,ant2,patch_name))        
            pass
        ns.predict(ant1, ant2) << Meq.Add(cache_num_active_parents=1,children=deepcopy(corrupted_patch_vis_list))    
#        ns.predict_patches(ant1, ant2) << Meq.Add(children=deepcopy(corrupted_patch_vis_list))    
#        ns.predict(ant1, ant2) << Meq.MatrixMultiply(ns.G(ant1),
#                                                     ns.predict_patches(ant1, ant2),
#                                                     ns.ctG(ant2))   
        pass
    pass







def forest_baseline_correct_trees(ns, interferometer_list, patch_name):
    for (ant1, ant2) in interferometer_list:
        ns.subtract(ant1, ant2) << (ns.spigot(ant1,ant2) - \
                                    ns.predict(ant1, ant2))
        ns.corrected(ant1,ant2) << \
                Meq.MatrixMultiply(Meq.MatrixInvert22(ns.J(ant1,patch_name)), #                               Meq.MatrixInvert22(ns.G(ant1)),
                                   ns.subtract(ant1,ant2), #                               Meq.MatrixInvert22(ns.ctG(ant2)),
                                   Meq.MatrixInvert22(ns.ctJ(ant2, patch_name)))
        pass
    pass





def forest_sum_of_phases(ns, station_list, patch_name, coeff):
    phase_list = []
    for station in station_list:
        phase_list.append("JP:"+str(station)+":"+patch_name+":"+coeff)
        pass
    ns.SumOfPhases(patch_name, coeff)  << Meq.Add(children=phase_list)  
    ns.ce("Phases", patch_name, coeff) << Meq.Condeq(0.0, ns.SumOfPhases(patch_name, coeff))    
    pass





def get_WSRT_reduntant_baselines():
    redundant=[[[11,12], [13,14]]]
    print(redundant[0])
    for sep in range(1,10):
        r=[]
        for s in range(1,11-sep):
            r.append([s,s+sep])
            pass
        print(r)
        redundant.append(r)
        pass
    return redundant




def forest_solver(ns, interferometer_list, station_list, patch_list, input_column='DATA'):
    ce_list = []
    # Measurements
    for (ant1,ant2) in interferometer_list:
        ns.spigot(ant1, ant2) << Meq.Spigot(station_1_index=ant1-1,
                                            station_2_index=ant2-1,
                                            flag_bit=4,
                                            input_col=input_column)
        ns.ce(ant1, ant2) << Meq.Condeq(ns.spigot(ant1, ant2),
                                        ns.predict(ant1, ant2))
        ce_list.append(ns.ce(ant1, ant2))
        pass
    # Constraints
    # Phase constraints
    for patch in patch_list:
        forest_sum_of_phases(ns, station_list, patch, "11");
        forest_sum_of_phases(ns, station_list, patch, "22");
        ce_list.append(ns.ce("Phases", patch, "11"));
        ce_list.append(ns.ce("Phases", patch, "22"));
        pass

        # Redundancy constraints: to be added
        
    # set up a non-default child poll order for most efficient 
    # parallelization
    # (i.e. poll child 1:2, 3:4, 5:6, ..., 13:14,
    # then the rest)
    cpo = [];
    for i in range(len(station_list)/2):
      (ant1,ant2) = station_list[i*2:(i+1)*2];
      cpo.append(ns.ce(ant1,ant2).name);
    
    ns.solver << Meq.Solver(children=ce_list,child_poll_order=cpo);    
    pass



def forest_create_sink_sequence(ns, interferometer_list, output_column='PREDICT'):
    ns.VisDataMux << Meq.VisDataMux;
    for (ant1, ant2) in interferometer_list:
        ns.sink(ant1,ant2) << Meq.Sink(station_1_index=ant1-1,
                                       station_2_index=ant2-1,
                                       flag_bit=4,
                                       corr_index=[0,1,2,3],
                                       flag_mask=-1,
                                       output_col=output_column,
                                       children=[Meq.ReqSeq(ns.solver,
                                                 ns.corrected(ant1, ant2),
                                                 result_index=1)]
                                       )
        pass
    pass
    ns.VisDataMux.add_children(*[ns.sink(ant1,ant2) for (ant1, ant2) in interferometer_list]);
    ns.VisDataMux.add_stepchildren(*[ns.spigot(ant1,ant2) for (ant1, ant2) in interferometer_list]);



def _define_forest(ns):
    mep_table_name      = '3C343.mep'
    source_mep_tablename= 'sourcemodel.mep'
    station_list        = list(range(1, 14+1))
    interferometer_list = [(ant1, ant2) for ant1 in station_list for ant2 in station_list if ant1 < ant2]

    source_model,extra_sources = create_initial_source_model(tablename=source_mep_tablename,extra_sources_filename='extra_sources.txt')
    
# Ehrm... brute force. The "right" way of doing this is to
# assign the extra sources to patches depending on their proximity
# to the patch centre    
    patch_source_lists= {'centre':[source_model[0]]+extra_sources,
                         'edge':[source_model[1]]}

    forest_measurement_set_info(ns, len(station_list))

    for source in source_model+extra_sources:
        forest_source_subtrees(ns, source)
        pass
        
    for station in station_list:
        forest_station_jones(ns, station, mep_table_name)
        pass
        
    for (name, list) in patch_source_lists.items():
        forest_clean_patch_predict_trees(ns, name, list, station_list)
        for station in station_list:
            forest_station_patch_jones(ns, station, name, mep_table_name)
            pass
        pass

    forest_baseline_predict_trees(ns, interferometer_list,
                                  list(patch_source_lists.keys()))
    forest_solver(ns, interferometer_list, station_list, list(patch_source_lists.keys()))
    forest_baseline_correct_trees(ns, interferometer_list, 'centre')
    forest_create_sink_sequence(ns, interferometer_list)
    pass




def create_inputrec(msname, tile_size=1500,short=False):
    boioname = "boio."+msname+"."+str(tile_size);
    # if boio dump for this tiling exists, use it
    # (skip this for now)
    if not short and os.access(boioname,os.R_OK):
      rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
    # else use MS, but tell the event channel to record itself to boio file
    else:
      rec = record();
      rec.ms_name          = msname
      rec.data_column_name = 'DATA'
      rec.tile_size        = tile_size
      rec.selection = record(channel_start_index=25,
                             channel_end_index=40,
                             channel_increment=1,
#                             selection_string='ANTENNA1<6 && ANTENNA2<6')
#                             selection_string='TIME_CENTROID < 4472026000')
                             selection_string='')
      if short:
        rec.selection.selection_string = 'TIME_CENTROID < 4472026000';
      else:
        rec.record_input = boioname;
      rec = record(ms=rec);
    rec.python_init='MAB_read_msvis_header.py';
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


#def _test_forest(mqs, parent):
#    pass
    
def _tdl_job_8_evaluate_parms_over_reference_domain (mqs,parent):
  """Executes the 'verifier' node over the saved reference domain.
Assuming this is successful, you may examine the children of the verifier
node to compare past and current solutions.""";
  #if _reference_cells is None:
  #  raise RuntimeError,"""Reference domain not loaded, please run a source
  #flux fit and save the domain.""";
  #req = meq.request(_reference_cells,rqtype='ev');
  #mqs.clearcache('solver');
  #mqs.execute('verifier',req,wait=False);
  msname   = '3C343.MS'
  inputrec = create_inputrec(msname,tile_size=1500)
  req = meq.request();
  req.input  = inputrec;
  mqs.clearcache('verifier');
  mqs.clearcache('VisDataMux');
  mqs.execute('verifier',req,wait=(parent is None));
  pass

def _tdl_job_9_clear_all_node_caches (mqs,parent):
  """Clears all caches in the tree""";
  mqs.clearcache('solver');
  mqs.clearcache('VisDataMux');


def _tdl_job_1_source_flux_fit_no_calibration(mqs,parent,write=True):
    """This solves for the I and Q fluxes of the two sources,
    over the entire MS. 
    """;
    msname          = '3C343.MS'
    inputrec        = create_inputrec(msname,tile_size=1500)
    outputrec       = create_outputrec()

    source_list,extra_sources = create_initial_source_model(extra_sources_filename='extra_sources.txt')

    print(inputrec)
    print(outputrec)

    solvables = []
    for source in source_list+extra_sources:
        solvables.append('stokes:I:'+source.name)
        solvables.append('stokes:Q:'+source.name)
        pass
    print(solvables)
    for s in solvables:
        publish_node_state(mqs, s)
        pass
    
    publish_node_state(mqs, 'solver')

    solver_defaults = create_solver_defaults(solvable=solvables)
    print(solver_defaults)
    set_MAB_node_state(mqs, 'solver', solver_defaults)
    
    req = meq.request();
    req.input  = inputrec;
    if write:
      req.output = outputrec;
    # parent=None means no GUI, so wait for request to complete
    mqs.clearcache('verifier');
    mqs.clearcache('VisDataMux');
    mqs.execute('VisDataMux',req,wait=(parent is None));
    pass






#   PHASES    PHASES     PHASES


def _tdl_job_2_phase_solution_with_given_fluxes_all(mqs,parent,write=True):
    msname          = '3C343.MS'
    inputrec        = create_inputrec(msname, tile_size=100)
    outputrec       = create_outputrec()

    station_list = list(range(1,15))
    patch_list   = ['centre', 'edge']
    print(inputrec)
    print(outputrec)

    solvables = []
    for station in station_list:
        for patch in patch_list:
            solvables.append('JP:'+str(station)+':'+patch+':11')
            solvables.append('JP:'+str(station)+':'+patch+':22')
            pass
        pass    
    print(solvables)
    
    publish_node_state(mqs, 'JP:2:centre:11')
    publish_node_state(mqs, 'JP:2:edge:11')
    publish_node_state(mqs, 'solver')
    publish_node_state(mqs, 'corrected:2:11')
    
    solver_defaults = create_solver_defaults(solvable=solvables)
    print(solver_defaults)
    set_MAB_node_state(mqs, 'solver', solver_defaults)
    
    req = meq.request();
    req.input  = inputrec;
    # req.input.max_tiles = 1;  # this can be used to shorten the processing, for testing
    if write:
      req.output = outputrec;
    mqs.clearcache('verifier');
    mqs.clearcache('VisDataMux');
    mqs.execute('VisDataMux',req,wait=(parent is None));
    pass


#   GAINS     GAINS      GAINS    

def _tdl_job_3_gain_solution_with_given_fluxes(mqs, parent,write=True):
    msname          = '3C343.MS'
    inputrec        = create_inputrec(msname, tile_size=100)
    outputrec       = create_outputrec()

    source_list  = create_initial_source_model()
    station_list = list(range(1,15))
    patch_list   = ['centre', 'edge']
    print(inputrec)
    print(outputrec)

    solvables = []
    for station in station_list:
        for patch_name in patch_list:
            solvables.append('JA:'+str(station)+':'+patch_name+':11')
            solvables.append('JA:'+str(station)+':'+patch_name+':22')
            pass
        pass
    print(solvables)
    
    publish_node_state(mqs, 'JA:2:centre:11')
    publish_node_state(mqs, 'JA:2:edge:11')
    publish_node_state(mqs, 'solver')
    publish_node_state(mqs, 'corrected:2:11')
    
    solver_defaults = create_solver_defaults(solvable=solvables)
    print(solver_defaults)
    set_MAB_node_state(mqs, 'solver', solver_defaults)
    
    req = meq.request();
    req.input  = inputrec;
    # req.input.max_tiles = 1;  # this can be used to shorten the processing, for testing
    if write:
      req.output = outputrec;
    mqs.clearcache('verifier');
    mqs.clearcache('VisDataMux');
    mqs.execute('VisDataMux',req,wait=(parent is None));
    pass



# 
# 
# def _tdl_job_phase_solution_with_given_fluxes_edge(mqs, parent):
#     msname          = '3C343.MS'
#     inputrec        = create_inputrec(msname, tile_size=10)
#     outputrec       = create_outputrec()
# 
#     source_list  = create_initial_source_model()
#     station_list = range(1,15)
#     patch_list   = ['centre', 'edge']
#     print inputrec
#     print outputrec
# 
#     solvables = []
#     for station in station_list:
#         solvables.append('JP:'+str(station)+':'+patch_list[1]+':11')
#         solvables.append('JP:'+str(station)+':'+patch_list[1]+':22')
#         pass
#     print solvables
#     
#     publish_node_state(mqs, 'JP:9:edge:11')
#     publish_node_state(mqs, 'solver')
#     
#     solver_defaults = create_solver_defaults(solvable=solvables)
#     print solver_defaults
#     set_MAB_node_state(mqs, 'solver', solver_defaults)
#     
#     req = meq.request();
#     req.input  = record(ms=inputrec,python_init='MAB_read_msvis_header.py');
#     req.output = record(ms=outputrec);
#     mqs.execute('VisDataMux',req,wait=False);
#     pass
# 
# 
# 
# def _tdl_job_phase_solution_with_given_fluxes_centre(mqs, parent):
#     msname          = '3C343.MS'
#     inputrec        = create_inputrec(msname, tile_size=10)
#     outputrec       = create_outputrec()
# 
#     source_list  = create_initial_source_model()
#     station_list = range(1,15)
#     patch_list   = ['centre', 'edge']
#     print inputrec
#     print outputrec
# 
#     solvables = []
#     for station in station_list[1:]:
#         solvables.append('JP:'+str(station)+':'+patch_list[0]+':11')
#         solvables.append('JP:'+str(station)+':'+patch_list[0]+':22')
#         pass
#     print solvables
#     
#     publish_node_state(mqs, 'JP:9:centre:11')
#     publish_node_state(mqs, 'solver')
#     
#     solver_defaults = create_solver_defaults(solvable=solvables)
#     print solver_defaults
#     set_MAB_node_state(mqs, 'solver', solver_defaults)
#     
#     req = meq.request();
#     req.input  = record(ms=inputrec,python_init='MAB_read_msvis_header.py');
#     req.output = record(ms=outputrec);
#     mqs.execute('VisDataMux',req,wait=False);
#     pass
# 
# 




Settings.forest_state.cache_policy = 1  # 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = False

if __name__ == '__main__':

    
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);

   
    ns.Resolve();
    pass
