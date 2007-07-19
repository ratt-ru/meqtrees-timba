# script_name = 'MG_AGW_visu.py'

# Short description:
#   Tests the Meqtree cwvisualization nodes

# Keywords: ....

# Author: Tony Willis (AGW), DRAO

# History:
# - 8 Oct 2006: first version checked in

# Copyright: The MeqTree Foundation

# standard preamble

#% $Id$ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
from Timba.Contrib.OMS.IfrArray import IfrArray
 
# bookmark
Settings.forest_state = record(bookmarks=[
  record(name='spigots',page=[
    record(viewer="Result Plotter",udi="/node/spigot:1:2",pos=(0,0)),
#   record(viewer="Result Plotter",udi="/node/spigot:1:3",pos=(0,1)),
#   record(viewer="Result Plotter",udi="/node/spigot:1:4",pos=(0,2)),
#   record(viewer="Result Plotter",udi="/node/spigot:1:5",pos=(1,0)),
#   record(viewer="Result Plotter",udi="/node/spigot:2:3",pos=(1,1)),
#   record(viewer="Result Plotter",udi="/node/spigot:2:4",pos=(1,2)),
#   record(viewer="Result Plotter",udi="/node/spigot:2:5",pos=(2,0)),
#   record(viewer="Result Plotter",udi="/node/spigot:3:4",pos=(2,1)),
#   record(viewer="Result Plotter",udi="/node/spigot:3:5",pos=(2,2)),
    record(viewer="Result Plotter",udi="/node/data1",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/data2",pos=(0,2)),
    record(viewer="Result Plotter",udi="/node/data3",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/data4",pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/data5",pos=(1,2)),
  ]),
]);

# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

def _define_forest (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  num_stations = 5
  stations = range(1,num_stations+1)
  array = IfrArray(ns,stations)

# create spigots
  i = 0
  first = True
  for sta1,sta2 in array.ifrs():
    spigot = ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                                 station_2_index=sta2-1,
                                                 flag_bit=4,
                                                 input_col='DATA');

    sink = ns.sink(sta1,sta2) << Meq.Sink(station_1_index=sta1-1,
                                       station_2_index=sta2-1,
                                       corr_index=[0,1,2,3],
                                       output_col='PREDICT',
                                       children= ns['reqseq']
                                       )

    ns['mean'+str(i)] << Meq.Mean(spigot)
    ns['selector'+str(i)] << Meq.Selector(ns['mean'+str(i)],index=1)
    ns['selector'+str(i+10)] << Meq.Selector(ns['mean'+str(i)],index=2)
    if first:
      ns['selectora'] << Meq.Selector(spigot,index=0)
      ns['selectorb'] << Meq.Selector(spigot,index=3)
      first = False
    i = i + 1

# create visualization attribute records
  attrib_xx = record(plot=record())
  attrib_yy = record(plot=record())
  attrib_xx1 = record(plot=record())
  attrib_yy1 = record(plot=record())
  attrib_xx2 = record(plot=record())
  attrib = record(plot=record())
  attrib_xx['plot'] = record(color="blue", style="cross", plot_type= "spectra", label="xx",  size=1)
  ns['data1'] << Meq.DataCollect(ns['selectora'], top_label=hiid('visu'), attrib=attrib_xx)
  attrib_yy['plot'] = record(color="red", style="cross", plot_type= "spectra", label="yy",  size=1)
  ns['data2'] << Meq.DataCollect(ns['selectorb'], top_label=hiid('visu'),  attrib=attrib_yy)
  attrib_xx1['plot'] = record(color="blue", style="cross", plot_type= "realvsimag", label="xx",  size=1)
  ns['data3'] << Meq.DataCollect(ns['selectora'], top_label=hiid('visu'), attrib=attrib_xx1)
  attrib_yy1['plot'] = record(color="red", style="cross", plot_type= "realvsimag", label="yy",  size=1)
  ns['data4'] << Meq.DataCollect(ns['selectorb'], top_label=hiid('visu'), attrib=attrib_yy1)
  attrib_xx2['plot'] = record(color="blue", style="cross", plot_type= "spectra", label="xx",  size=1)
  ns['data5'] << Meq.DataCollect(ns['data1'], ns['data2'], top_label=hiid('visu'), attrib=attrib_xx2)

  visdatamux = ns['VisDataMux'] << Meq.VisDataMux;
  visdatamux.add_stepchildren(*[ns.spigot(*ifr) for ifr in array.ifrs()]);
  visdatamux.add_children(*[ns.sink(*ifr) for ifr in array.ifrs()]);

  ns['reqseq'] = Meq.ReqSeq(ns['data1'], ns['data2'], ns['data3'], ns['data4'], ns['data5'], result_index=4)


def create_inputrec(msname, tile_size=1500,short=False):
  rec = record();
  rec.ms_name          = msname
  rec.data_column_name = 'DATA'
  rec.tile_size        = tile_size
  rec.selection = record(channel_start_index=0,
                             channel_end_index=15,
                             channel_increment=1,
                             selection_string='')
  rec.selection.selection_string = '';
  rec = record(ms=rec)
  return rec

def create_outputrec(output_column='CORRECTED_DATA'):
    rec=record()
    rec.write_flags=False
    rec.predict_column=output_column
    return record(ms=rec);


def _test_forest (mqs,parent):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  msname          = 'TEST_CLAR_27-480.MS'
  inputrec        = create_inputrec(msname, tile_size=96)
  outputrec       = create_outputrec()
  print 'input record ', inputrec
  req = meq.request();
  req.input  = inputrec;
  req.output  = outputrec;
  mqs.clearcache('VisDataMux');
  print 'VisDataMux request is ', req
  mqs.execute('VisDataMux',req,wait=(parent is None));

# The following is the testing branch, executed when the script is run directly
# via 'python script.py'
if __name__ == '__main__':
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
