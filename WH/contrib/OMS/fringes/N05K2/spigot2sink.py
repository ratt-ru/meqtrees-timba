from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.OMS.IfrArray import IfrArray
from Timba.Contrib.OMS.Observation import Observation
from Timba.Contrib.OMS import Bookmarks

# MS name
TDLRuntimeOption('msname',"MS",["n05k2.ms"]);

TDLRuntimeOption('input_column',"Input MS column",["DATA","MODEL_DATA","CORRECTED_DATA"],default=0);
TDLRuntimeOption('output_column',"Output corrected data to MS column",[None,"DATA","MODEL_DATA","CORRECTED_DATA"],default=3);
TDLRuntimeOption('tile_size',"Tile size (timeslots)",[1,5,10,20,30,60,120]);

TDLRuntimeOption('field_index',"Field ID",[0,1,2,3,4]);
TDLRuntimeOption('ddid_index',"Data descrition (band) ID",[0,1,2,3]);

TDLCompileOption('stations_list',"Station list",[[1,2,3,4,7,8]]);

time0 = 4637030102.12;
selection_string = "TIME < %20f"%(time0+15*60);

# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted visibilities 1',page=Bookmarks.PlotPage(
      ["spigot:1:2","spigot:1:3"],
      ["spigot:1:4","spigot:1:7"]
  )),
  record(name='Predicted visibilities 2',page=Bookmarks.PlotPage(
      ["spigot:2:3","spigot:2:4"],
      ["spigot:3:4","spigot:4:7"]
  )),
]);


def _define_forest(ns):
  # create array model
  array = IfrArray(ns,stations_list);
  observation = Observation(ns);
  
  for sta1,sta2 in array.ifrs():
    spigot = ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                                 station_2_index=sta2-1,
                                                 flag_bit=4,
                                                 input_col='DATA');
    ns.sink(sta1,sta2) << Meq.Sink(station_1_index=sta1-1,
                                   station_2_index=sta2-1,
                                   flag_bit=4,
                                   corr_index=[0,1,2,3],
                                   flag_mask=-1,
                                   output_col='PREDICT',
                                   children=spigot
                                   );
                                   
  # create visdatamux
  global _vdm;
  _vdm = ns.VisDataMux << Meq.VisDataMux;
  ns.VisDataMux.add_children(*[ns.sink(*ifr) for ifr in array.ifrs()]);
  ns.VisDataMux.add_stepchildren(*[ns.spigot(*ifr) for ifr in array.ifrs()]);


def create_inputrec ():
  rec = record();
  rec.ms_name          = msname;
  rec.data_column_name = input_column;
  rec.tile_size        = tile_size;
  rec.selection =  record();
  rec.selection.ddid_index       = ddid_index;
  rec.selection.field_index      = field_index;
  rec.selection.selection_string = selection_string;
  rec = record(ms=rec);
  rec.python_init='read_msvis_header.py';
#  rec.mt_queue_size = ms_queue_size;
  return rec;

def create_outputrec ():
  rec=record()
#  rec.mt_queue_size = ms_queue_size;
  rec.write_flags=False
  rec.predict_column=output_column;
  return record(ms=rec);

def _test_forest (mqs,parent):
  req = meq.request();
  req.input = create_inputrec();
  req.output = create_outputrec();

  mqs.execute('VisDataMux',req,wait=False);


Settings.forest_state.cache_policy = 100 #100
Settings.orphans_are_roots = True

if __name__ == '__main__':
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();
  pass
